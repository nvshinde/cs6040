import os
import numpy as np
import time

class Packet():
    def __init__(self, sid, arrival_time, depart_time, pkt_len) -> None:
        self.len = pkt_len
        self.arrival_time = arrival_time
        self.depart_time = depart_time
        self.finish_num = None
        self.src_id = sid
    
    def __repr__(self) -> str:
        return(f"PKT: SID: {self.src_id}, FN: {self.finish_num}")

def source_fn(sid, q, virt_tm, data, file_lock):
    graph = []
    print(f"Source {sid} started. PID: {os.getpid()}")

    tb = data[sid]['tb'] * data['T']                                    # Begin generation time
    te = data[sid]['te'] * data['T']                                    # End generation time
    
    total_packets = 0                                                   # Total packets generated
    total_generated_data = 0                                            # Total packet length units generated.
    packets_dropped = 0                                                 # Total packets dropped due to full queue

    while virt_tm.value <= data['T']:
        if(tb <= virt_tm.value <= te):
            iat = np.random.exponential(scale=(1/data[sid]['p']))
            next = virt_tm.value + iat
            while next > virt_tm.value:                                 # Wait till next packet generation
                time.sleep(0.0001)                                      # Avoid busy waiting

            plen = np.random.randint(int(data[sid]['lmin']), int(data[sid]['lmax']+1))          # Packet len uniformly distributed
            pkt = Packet(sid=sid, arrival_time=virt_tm.value, depart_time=None, pkt_len=plen)   # Generate a packet with length plen
            try:
                q.put(pkt, block=False)
            except:                                                     # Full queue, packet is dropped
                packets_dropped += 1
            total_generated_data += plen
            total_packets += 1
            graph.append((virt_tm.value, 1))
    
    with file_lock:
        with open("metrics/src.csv", 'a') as f:
            f.write(f"{sid}, {total_packets}, {total_generated_data}, {packets_dropped}\n")
    
    with open("metrics/" + f"src{sid}-graph.txt", 'w') as f:
        f.write("time, val\n")
        for item in graph:
            f.write(f"{item[0]}, {item[1]}\n")
