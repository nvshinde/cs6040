import os.path
import argparse
import numpy as np
import multiprocessing as mp                                                    # for sources. Not using multithreading due to GIL
import time

import scheduler
import server
import source
import pprint

VIRT_CLOCK_INCREMENT = 0.002                                                    # Virtual clock to real clock mapping

def parse_input_file(input_f):                                                  # Parse input data
    input_data = {}
    with open(input_f, 'r') as f:
        """Read N, T, C, B"""
        key_vals = f.readline().strip().split()
        for key_val in key_vals:
            key, val = key_val.split("=")
            input_data[key] = int(val)
        
        """Read each source params"""
        for src in range(input_data['N']):
            source = {}
            data = f.readline().strip().split()
            source["p"], source['lmin'], source['lmax'], source['w'], source['tb'], source['te'] = map(float, data)
            input_data[src] = source

    return input_data

def virtual_clock(virt_tm, data):                                               # Virtual clock process.
    last_tm = 0
    while virt_tm.value <= data['T']:
        time.sleep(10/1000000)                                                  # 10us real time == VIRT_CLOCK_INCREMENT virtual time
        virt_tm.value += VIRT_CLOCK_INCREMENT
        if (virt_tm.value - last_tm) > 1000:
            print(f"T: {virt_tm.value}")
            last_tm = virt_tm.value

def run_simulation(input_f, output_f):

    data = parse_input_file(input_f)

    # TODO: do queue size as per len units. In current implmentation, only B pkts of max len can be put, but as per requirement, more that B packts of smaller len can be present
    q = mp.Queue(maxsize=1)                                                     # Input buffer
    p_rx, p_tx = mp.Pipe()                                                      # Pipe between scheduler and server

    file_lock = mp.Lock()
    with file_lock:
        with open("metrics/src.csv", 'w') as f:
                f.write("Source, Packets Gen, Bg, Dropped\n")

    virtual_time = mp.Value('f', 0)                                             # Shared. virtual_clock updates this()
    pkts_in_server = mp.Value('i', 0)                                           # Shared. Server uses this as counting semaphore

    server_proc = mp.Process(target=server.server_fn, args=(p_rx, p_tx, virtual_time, data, pkts_in_server))
    scheduler_proc = mp.Process(target=scheduler.scheduler_fn, args=(q, p_tx, virtual_time, data, pkts_in_server))
    virtual_clock_proc = mp.Process(target=virtual_clock, args=(virtual_time, data))

    sources = []
    for s in range(data['N']):
        src_proc = mp.Process(target=source.source_fn, args=(s, q, virtual_time, data, file_lock))
        sources.append(src_proc)
        src_proc.start()

    server_proc.start()
    scheduler_proc.start()
    virtual_clock_proc.start()

    for s, src in enumerate(sources):
        print(f"src_proc {s}: {src.name}. PID: {src.pid}")
    print(f"server_proc: {server_proc.name}. PID: {server_proc.pid}")
    print(f"scheduler_proc: {scheduler_proc.name}. PID: {scheduler_proc.pid}")
    print(f"vc_proc: {virtual_clock_proc.name}. PID: {virtual_clock_proc.pid}")

    for src in sources:                                                         # Wait for sources to finish
        src.join()
    
    virtual_clock_proc.join()                                                   # Wait for other processes to finish
    scheduler_proc.join()
    p_tx.close()
    server_proc.join()
   
    src_metrics = {}                                                            # Post processing. Per source metrics
    with open("metrics/src.csv", 'r') as f:
        f.readline()
        for _ in range(data['N']):
            src, pkts_gen, bg, dropped = map(int, f.readline().strip().split(','))
            details = {'pkts_gen': pkts_gen, 'bg': bg, 'dropped': dropped}
            src_metrics[src] = details

    with open("metrics/server.csv", 'r') as f:
        f.readline()
        for _ in range(data['N']):
            src, pkts_txd, bt, mean_delay, server_util = map(float, f.readline().strip().split(','))
            src_metrics[src]['pkts_txd'] = int(pkts_txd)
            src_metrics[src]['bt'] = int(bt)
            src_metrics[src]['mean_delay'] = mean_delay
            src_metrics[src]['server_util'] = server_util
    pprint.pprint(src_metrics)

    with open(output_f, 'w') as f:
        f.write("Conn ID, Bg, Bt, Bt/Bg, Fraction of link BW, Mean pkt delay, Pkt drop prob\n")
        for s in range(data['N']):
            f.write(f"{s}, \
{src_metrics[s]['bg']}, \
{src_metrics[s]['bt']}, \
{(src_metrics[s]['bt']/src_metrics[s]['bg']):.4f}, \
{(src_metrics[s]['bt']/sum([src_metrics[x]['bt'] for x in range(data['N'])])):.4f}, \
{(src_metrics[s]['mean_delay']):.4f}, \
{((src_metrics[s]['pkts_gen'] - src_metrics[s]['pkts_txd'])/src_metrics[s]['pkts_gen']):.4f}\n")
    
    # Post processing. System level metrics
    # TODO: Server Utilization
    # TODO: Fairness Index
    # TODO: RFB every 10000 time units
    with open(output_f, 'a') as f:
        mdelay = 0
        mdropped = 0
        tGen = 0
        for s in src_metrics.keys():
            mdelay += src_metrics[s]['mean_delay']
            mdropped += (src_metrics[s]['pkts_gen'] - src_metrics[s]['pkts_txd'])
            tGen += src_metrics[s]['pkts_gen']
  
        f.write(f"\n\
Mean packet delay: {(mdelay/data['N']):.4f}\n\
Mean packet drop probability: {(mdropped/tGen):.4f}\n\
Server Utilizaition: {src_metrics[0]['server_util']}\n\
")
    print("Done!!!")

if __name__ == "__main__":
    np.random.seed(0)
    mp.set_start_method('fork')
    parser = argparse.ArgumentParser(prog="WFQ Scheduler", description="")
    parser.add_argument('-inp', help="Input file", action="store", type=str, required=True)
    parser.add_argument('-out', help="Output file", action="store", type=str, required=True)

    args = parser.parse_args()

    if not os.path.isfile(args.inp):
        print("Input file does not exist!")
        exit()
    
    run_simulation(args.inp, args.out)