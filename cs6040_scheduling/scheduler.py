def compute_FN(last_FN, R_t, packet, data):
    return max(last_FN, R_t) + packet.len/data[packet.src_id]['w']

def scheduler_fn(q, tx_pipe, virt_tm, data, pkts_in_server):
    R_tp = [0, 0]                                                           # Previous R_t [R_tp, tp]
    R_t = [0, 0]                                                            # Round no. [R_t, t]
    active_flows = set()                                                    # Active flows
    Rdash_t = float('inf')                                                  # Slope
    last_rx_pkt_finish_nos = [0 for _ in range(data['N'])]                  # FNs of last packet of each flow. Will be the max FN for that flow
    # last_pkts_sent_per_flow = [None for _ in range(data['N'])]
    curr_time = 0
    while virt_tm.value <= data['T']:                                       # Run till simulation ends
        curr_time = virt_tm.value
        
        if pkts_in_server.value < data['B']:                                # Space available in buffer. pkts_in_server is semaphore
            try:
                packet = q.get(block=False)
                if not packet:                                              # Packet is not available, continue
                    continue
                if R_t[1] <  curr_time:                                    # Update Rt
                    if Rdash_t == float('inf'):
                        R_t[0] = R_tp[0]
                    else:
                        R_t[0] = R_tp[0] + Rdash_t*(curr_time - R_tp[1])
                    R_t[1] = curr_time
                    R_tp[0], R_tp[1] = R_t[0], R_t[1]
                
                curr_FN = compute_FN(last_FN=last_rx_pkt_finish_nos[packet.src_id], R_t=R_t[0], packet=packet, data=data)                                                  # Compute FN
                packet.finish_num = curr_FN
                if curr_FN >= last_rx_pkt_finish_nos[packet.src_id]:
                    last_rx_pkt_finish_nos[packet.src_id] = curr_FN

                temp = 0                                                    # Update Active flows and R't
                for src, fn in enumerate(last_rx_pkt_finish_nos):
                    if fn > R_t[0]:                                         # If flow is active
                        active_flows.add(src)
                        temp += data[src]['w']
                    else:
                        active_flows.discard(src)
                if temp:
                    Rdash_t = 1/temp                                        # Otherwise, R't stays infinity

                tx_pipe.send(packet)                                        # Send packet to server
            except:                                                         # No packet available to process
                pass
                                
        if R_t[1] < curr_time:                                             # Update Rt and R't again with each loop; Thus no need for iterated deletion
            temp = 0
            for src, fn in enumerate(last_rx_pkt_finish_nos):               # Update active flows, R't
                if fn > R_t[0]:
                    active_flows.add(src)
                    temp += data[src]['w']
                else:
                    active_flows.discard(src)
            if temp:
                Rdash_t = 1/temp

            if Rdash_t == float('inf'):                                     # Update Rt
                R_t[0] = R_tp[0]
            else:
                R_t[0] = R_tp[0] + Rdash_t*(curr_time - R_tp[1])
            R_t[1] = curr_time
            R_tp[0], R_tp[1] = R_t[0], R_t[1]

    print("Scheduler Done")
    tx_pipe.close()