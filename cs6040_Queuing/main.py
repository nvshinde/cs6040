import argparse
import random
import numpy as np
import pprint
import time

input_queues = {}
output_queues = {}

class Packet:
    def __init__(self, arrival_time, inport, outport) -> None:
        self.arrival_time = arrival_time
        self.depart_time = None
        self.inport = inport
        self.outport = outport
        self.delay = 0


# Traffic Generation
def traffic_gen(num_ports, pktgenprob, curr_slot):
    """Generate a packet for slot 'curr_slot' for every input port"""
    global input_queues
    packets = []
    for in_port in range(num_ports):
        """Packet arrives at in_port with prob. pktgenprob."""
        if np.random.binomial(n=1, p=pktgenprob):
            out_port = np.random.randint(0, num_ports)
            arrival_time = float(format(np.random.uniform(curr_slot+0.001, curr_slot+0.01), '.3f'))
            packet = Packet(arrival_time=arrival_time, inport=in_port, outport=out_port)
            # packets.append((in_port, packet))
            """Enqueue each packet in the input queue"""
            input_queues[in_port].append(packet)

# Scheduling
def scheduling(numports, q_type):
    sched_delay_start =  time.clock_gettime_ns(time.CLOCK_BOOTTIME)
    global input_queues
    global output_queues

    if q_type == "NOQ":
        """No Queueing"""

        """Temp DS; For each output port, create a queue"""
        temp_queues = {out_port: [] for out_port in range(numports)}
        for in_port, packets in input_queues.items():
            for packet in packets:
                temp_queues[packet.outport].append(packet)
        
        """Choose one packet on each of output ports"""
        for out_port in range(numports):
            if temp_queues[out_port]:
                """Choose a random packet from all pkts destined to out_port"""
                packet = np.random.choice(temp_queues[out_port])

                sched_delay_end = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                delay_ns = sched_delay_end - sched_delay_start
                packet.delay += delay_ns
                output_queues[out_port].append(packet)

    elif q_type == "INQ":
        """Input Queuing. Default."""
        pass
    elif q_type == "CIOQ":
        pass
    else:
        print("Huh?")

    # pprint.pprint(output_queues)
    # for out_port, pkt in output_queues:
    #     print(f"Out: {out_port}, PKT: in: {pkt.inport}, out: {pkt.outport}, at: {pkt.arrival_time}, dt: {pkt.depart_time}")

def transmission(numports, q_type):
    global input_queues
    global output_queues

    if q_type == "NOQ":
        """Assuming switch backplane is N times faster"""

        """Calculate no. of pkts in HOL in each output queue"""
        """Here, in NOQ, each output queue will have one pkt only."""
        num_tx_rdy_pkts = 0
        for queue, pkts in output_queues.items():
            if pkts:
                num_tx_rdy_pkts += 1
            
        for i, (queue, pkts) in enumerate(output_queues.items()):
            for pkt in pkts:
                pkt.depart_time = (i+1)*(1 / numports)
                
                # TODO: calculate pkt delay
        
    elif q_type == "INQ":
        pass
    elif q_type == "CIOQ":
        pass
    else:
        print("Huh?")
    pass

def run(N, B, p, q, K, L, o, T):
    
    """DS to hold queues at input and output"""
    global input_queues 
    global output_queues
    
    input_queues = {ip: [] for ip in range(N)}
    output_queues = {op: [] for op in range(N)}

    for curr_slot in range(T):
        traffic_gen(num_ports=N, pktgenprob=p, curr_slot=curr_slot)
        scheduling(numports=N, q_type=q)
        transmission()
        
        for op, pkts in output_queues.items():
            for pkt in pkts:
                print(f"OP: {op}, PKT: i: {pkt.inport}, o: {pkt.outport}, at: {pkt.arrival_time}, dt: {pkt.depart_time}")
        
        if q == "NOQ":
            """Discard all packets in queues. No buffering"""
            input_queues = {queue: [] for queue in range(N)}
            output_queues = {queue: [] for queue in range(N)}
        elif q == "INQ":
            pass
        elif q == "CIOQ":
            pass
        else:
            print("Huh?")

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)

    parser = argparse.ArgumentParser(prog="Queuing in a Packet Switch",
                                     description="")
    parser.add_argument('-N', help="No. of ports in a switch. Default 8.", action="store", default=8, type=int)
    parser.add_argument('-B', help="Buffer size. Default 10.", action="store", default=10, type=int)
    parser.add_argument('-p', help="The probability that an input port will generate a packet in a given slot. Default 0.5.", action="store", default=0.5, type=int)
    parser.add_argument('-q', help="Queue type: 'NOQ', 'INQ', 'CIOQ'. Default 'INQ'.", action="store", default="INQ", type=str)
    
    # TODO: Add default values and help 
    parser.add_argument('-K', help="Knockout value. Default?", action="store", default=0, type=int)
    parser.add_argument('-L', help="inpq value. Default?", action="store", default=0, type=int)
    
    parser.add_argument('-o', help="Output file. Default 'out.txt'", action="store", default="out.txt", type=str)
    parser.add_argument('-T', help="Maxslots. This specifies the simulation time in slots. Default 10000", action="store", default=10000, type=int)

    args = parser.parse_args()

    run(args.N, args.B, args.p, args.q, args.K, args.L, args.o, args.T)