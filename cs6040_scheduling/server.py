import time
def server_fn(rx_pipe, tx_pipe, virt_tm, data, pkts_in_server):
    tx_pipe.close()

    scheduled_pkts = []                                                             # Priority queue. 
    last_end_time = 0                                                               # Last packet tx end time
    total_pkt_len = [0 for _ in range(data['N'])]                                   # Sum of pkts len for each src
    total_pkts_txd = [0 for _ in range(data['N'])]                                  # Total pkts txd from a src
    avg_pkt_delay = [0 for _ in range(data['N'])]                                   # Mean delay for each src
    flag = 0                                                                        # Check if pipe is closed
    server_utilization = 0
    graph = []
    fairness = []
    fairness_time = 0

    while virt_tm.value <= data['T']:                                               # Run till simulation time
        if len(scheduled_pkts) < data['B'] and not flag:                           # If space in buffer and pipe is open
            try:
                pkt = rx_pipe.recv()
                scheduled_pkts.append(pkt)
                pkts_in_server.value += 1                                           # Semaphore to count buffer space
            except EOFError:
                print("Pipe closed")
                flag = 1

        if virt_tm.value >= last_end_time:                                          # Send next packet after current packet is finished txd                                   
            next_pkt = None
            if scheduled_pkts:                                                      # If there are packets in buffer
                for pkt in scheduled_pkts:                                          # Get the pkt with smallest FN
                    if next_pkt == None:
                        next_pkt = pkt
                    else:
                        if pkt.finish_num < next_pkt.finish_num:
                            next_pkt = pkt

                scheduled_pkts.remove(next_pkt)                                     # Remove from buffer
                pkts_in_server.value -= 1                                           # Reduce semaphore
                last_end_time = virt_tm.value + next_pkt.len/data['C']
                next_pkt.depart_time = last_end_time
                total_pkt_len[next_pkt.src_id] += next_pkt.len
                total_pkts_txd[next_pkt.src_id] += 1
                avg_pkt_delay[next_pkt.src_id] += next_pkt.depart_time - next_pkt.arrival_time
                server_utilization += next_pkt.len/data['C']
                graph.append((virt_tm.value, last_end_time))
        
        # print(f"VT: {virt_tm.value}, FT:{fairness_time}")
        # # Fairness Measure
        # throughput = []
        # if virt_tm.value - fairness_time > 500:                                                          # Whenever 500 units pass
        #     print("here")
        #     fairness_time = virt_tm.value
        #     for src, data_units in enumerate(total_pkt_len):
        #         throughput.append(data_units/fairness_time)
        #     temp = (sum(throughput)**2)/(len(throughput)*(sum([x**2 for x in throughput])))
        #     fairness.append((fairness_time, temp))
        #     print(f"Fairness @ {fairness_time} is {temp}")
        
        time.sleep(0.0001)

    print("Simulation Ends.\nPackets not txd.: " + str(len(scheduled_pkts)))
    with open("metrics/server.csv", 'w') as f:
        f.write("Source, Packets txd, Bt, Mean delay, Server Utilization\n")
        for src, pkt_len_txd in enumerate(total_pkt_len):
            if total_pkts_txd[src] != 0:
                f.write(f"{src}, {total_pkts_txd[src]}, {pkt_len_txd}, {(avg_pkt_delay[src]/total_pkts_txd[src]):.4f}, {(server_utilization/data['T']):.4f}\n")
            else:
                f.write(f"{src}, {total_pkts_txd[src]}, {pkt_len_txd}, 0, {(server_utilization/data['T']):.4f}\n")
        
    # with open("metrics/fairness.csv",'w') as f:
    #     f.write("time, fairness\n")
    #     for item in fairness:
    #         f.write(f"{item[0]}, {item[1]}\n")

    with open('metrics/graph.txt', 'w') as f:
        for item in graph:
            f.write(f"{item[0]}, {item[1]}\n")
# TODO: Plot of graph of pkt tx. times. 1 when pkt is being txd. 0 when no pkt is being txd.