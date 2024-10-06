import argparse
import random
import numpy as np
import time

input_queues = {}
output_queues = {}
curr_slot_tx_pkts = []
port_utilization = {}
drop_prob = {}


mean_port_utilization = 0
CIOQ_drop_prob = 0

class Packet:
    def __init__(self, arrival_time, inport, outport) -> None:
        self.arrival_time = arrival_time
        self.depart_time = None
        self.inport = inport
        self.outport = outport
        self.total_delay = 0
        self.sched_delay = 0
    
    def __repr__(self):
        return (f"(PKT: ip: {self.inport}, op: {self.outport}, at: {self.arrival_time}, dt: {self.depart_time}, sd: {self.sched_delay}, td: {self.total_delay})")

def traffic_gen(num_ports, pktgenprob, curr_slot, q_type, B, L):
    """Generate a packet for slot 'curr_slot' for every input port"""
    global input_queues

    # TODO: Move to caller function
    if q_type == "NOQ":
        B = 1
    # if q_type == "CIOQ":
    #     B = L
    
    for in_port in range(num_ports):
        """Packet arrives at in_port with prob. pktgenprob."""
        if np.random.binomial(n=1, p=pktgenprob):
            out_port = np.random.randint(0, num_ports)
            arrival_time = float(format(np.random.uniform(curr_slot+0.001, curr_slot+0.01), '.3f'))
            packet = Packet(arrival_time=arrival_time, inport=in_port, outport=out_port)
            
            """Enqueue each packet in the input queue, only if buffer space available"""
            if len(input_queues[in_port]) <= B:
                input_queues[in_port].append(packet)

# Scheduling
def scheduling(numports, q_type, curr_slot, L, K, B):
    sched_delay_start =  time.clock_gettime_ns(time.CLOCK_BOOTTIME)
    global input_queues
    global output_queues
    global drop_prob
    
    if q_type == "NOQ":
        """Temp DS; For each output port, create a queue"""
        temp_queues = {out_port: [] for out_port in range(numports)}
        for in_port, packets in input_queues.items():
            """Only 1 pkt in NOQ"""
            if packets:
                temp_queues[packets[0].outport].append(packets[0])
        
        """Choose one packet on each of output ports"""
        for out_port in range(numports):
            if temp_queues[out_port]:
                """Choose a random packet from all pkts destined to out_port"""
                packet = np.random.choice(temp_queues[out_port])
                sched_delay_end = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                delay_ns = sched_delay_end - sched_delay_start
                packet.sched_delay += delay_ns
                output_queues[out_port].append(packet)

        """Clear the input queue, since pkt is in output queue"""
        input_queues = {in_port: [] for in_port in input_queues}
        
    elif q_type == "INQ":     
        """Temp DS; For each output port, create a queue"""
        temp_queues = {out_port: [] for out_port in range(numports)}
        for in_port, packets in input_queues.items():
            """Choose HOL pkt"""
            if packets:
                temp_queues[packets[0].outport].append(packets[0])
        
        """Choose one packet on each of output ports w/ lowest input port no."""
        for out_port in range(numports):
            if temp_queues[out_port]:
                """Choose packet with lowest inp port no. from all pkts destined to out_port"""
                packet = None
                for pkt in temp_queues[out_port]:
                    if not packet:
                        packet = pkt
                    else:
                        if pkt.inport < packet.inport:
                            packet = pkt
                        
                sched_delay_end = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                delay_ns = sched_delay_end - sched_delay_start
                packet.sched_delay += delay_ns
                output_queues[out_port].append(packet)

                """Dequeue that packet from the input queue"""
                input_queues[packet.inport].remove(packet)
                
    elif q_type == "CIOQ":
        """Temp DS; For each output port, create a queue"""
        temp_queues = {out_port: [] for out_port in range(numports)}
        for in_port, packets in input_queues.items():
            """Consider one possible pkts out of L packets"""
            if packets:
                # pkt = np.random.choice(packets[:min(L, len(packets))])
                pkt = np.random.choice(packets[:L])
                temp_queues[pkt.outport].append(pkt)
                
                """Dequeue that packet from the input queue"""
                input_queues[pkt.inport].remove(pkt)
                        
        """Choose K packets on each of output ports"""
        num_ports_gtK = 0
        for out_port in range(numports):
            if temp_queues[out_port]:
                """Choose only K packets"""
                packets = np.random.choice(temp_queues[out_port], K)
                
                """For drop prob."""
                if len(temp_queues[out_port]) > K:
                    num_ports_gtK += 1
                    
                sched_delay_end = time.clock_gettime_ns(time.CLOCK_BOOTTIME)
                delay_ns = sched_delay_end - sched_delay_start
                
                for pkt in packets:
                    pkt.sched_delay += delay_ns
                
                """Make sure output queue has space"""
                if len(output_queues[out_port]) < B:
                    packets = packets[:B-len(output_queues[out_port])]
                    output_queues[out_port].extend(packets)
        drop_prob[curr_slot] = num_ports_gtK/numports
    else:
        print("No such Q")

    # pprint.pprint(output_queues)
    # for out_port, pkt in output_queues:
    #     print(f"Out: {out_port}, PKT: in: {pkt.inport}, out: {pkt.outport}, at: {pkt.arrival_time}, dt: {pkt.depart_time}")

def transmission(curr_slot):
    global input_queues
    global output_queues
    global curr_slot_tx_pkts
    global port_utilization
               
    for queue, pkts in output_queues.items():
        if pkts:
            """Transmit HOL packet and remove from output queue"""
            pkt = output_queues[queue][0]
            pkt.depart_time = curr_slot + 1
            pkt.total_delay = pkt.depart_time - int(pkt.arrival_time)
            curr_slot_tx_pkts.append(pkt)
            port_utilization[queue] += 1
            output_queues[queue].remove(pkt)

def run(N, B, p, q, K, L, o, T):
    
    """DS to hold queues at input and output"""
    global input_queues 
    global output_queues
    global curr_slot_tx_pkts
    global port_utilization
    global drop_prob

    """Specific case as mentioned for INQ"""
    if q == "INQ":
        L = 1
    if q == "CIOQ":
        if L == None:
            L = int(0.4*N)
        if K == None:
            K = int(0.4*N)
    
    input_queues = {ip: [] for ip in range(N)}
    output_queues = {op: [] for op in range(N)}
    port_utilization = {op: 0 for op in range(N)}
    drop_prob = {slot: 0 for slot in range(T)}

    total_packet_delay = 0
    total_tx_pkts = 0
    for curr_slot in range(T):
        # print(f"=====================Slot {curr_slot}=====================")
        traffic_gen(num_ports=N, pktgenprob=p, curr_slot=curr_slot, q_type=q, B=B, L=L)
        scheduling(numports=N, q_type=q, curr_slot=curr_slot, L=L, K=K, B=B)
        transmission(curr_slot=curr_slot)
        
        total_tx_pkts += len(curr_slot_tx_pkts)
        for pkt in curr_slot_tx_pkts:
            total_packet_delay += pkt.total_delay
        curr_slot_tx_pkts = []
            
    mean_delay = round(total_packet_delay/total_tx_pkts, 3)
    
    mean_utilization = 0
    for port, utilization in port_utilization.items():
        mean_utilization += round(utilization/T, 3)
    mean_utilization /= N
    mean_utilization = round(mean_utilization, 3)
        
    if q == "NOQ" or q == "INQ":
        with open(o, '+a') as output_f:
            output_f.write(f"{N}\t{p}\t{q}\t{mean_delay}\t{mean_utilization}\n")
    if q == "CIOQ":
        """Drop. prob"""
        dp = 0
        for slot, prob in drop_prob.items():
            dp += prob
        dp /= T
        with open(o, '+a') as output_f:
            output_f.write(f"{N}\t{p}\t{L}\t{K}\t{q}\t{mean_delay}\t{mean_utilization}\t{dp}\n")
def gen_graphs():
    pass

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)

    parser = argparse.ArgumentParser(prog="Queuing in a Packet Switch",
                                     description="")
    parser.add_argument('-N', help="No. of ports in a switch. Default 8.", action="store", default=8, type=int)
    parser.add_argument('-B', help="Buffer size. Default 10.", action="store", default=10, type=int)
    parser.add_argument('-p', help="The probability that an input port will generate a packet in a given slot. Default 0.5.", action="store", default=0.5, type=float)
    parser.add_argument('-q', help="Queue type: 'NOQ', 'INQ', 'CIOQ'. Default 'INQ'.", action="store", default="INQ", type=str)
    
    parser.add_argument('-K', help="Switch Backplane speedup for CIOQ. Default 0.4*N", action="store", type=int)
    parser.add_argument('-L', help="Num buffered pkts at each i/p Q in CIOQ. Default 0.4*N", action="store", type=int)
    
    parser.add_argument('-o', help="Output file. Default 'out.txt'", action="store", default="out.txt", type=str)
    parser.add_argument('-T', help="Maxslots. This specifies the simulation time in slots. Default 10000", action="store", default=10000, type=int)
    parser.add_argument('-g', help="Generate graphs? Y/N. Default N", action="store", default="N", type=str)
    parser.add_argument('-gf', help="Graph data output file. Default graph.txt", action="store", type=str)

    args = parser.parse_args()

    run(args.N, args.B, args.p, args.q, args.K, args.L, args.o, args.T)
    
    if args.g == "Y":
        if args.q == "INQ" or args.q == "NOQ":
            for n in [2, 4, 8, 16, 32, 64, 100]:
                for p in [0.4, 0.6, 0.8, 1]:
                    run(n, args.B, p, args.q, args.K, args.L, args.gf, args.T)
        else:
            for n in [4, 8, 16, 32, 64, 100]:
                for p in [0.4, 0.6, 0.8, 1.0]:
                    for l in [0.4, 0.7, 1.0]:
                        for k in [0.4, 0.7, 1.0]:
                            run(n, args.B, p, args.q, int(k*n), int(l*n), args.gf, args.T)