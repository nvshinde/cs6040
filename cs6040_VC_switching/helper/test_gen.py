#!/usr/bin/python3

import argparse
import random

def generate_tc(max_delay, max_cap, topo_f=None, conn_f=None, n=2, l=1, r=0):
    # Generate topology.
    topo_dict = {'n':n, 'l': l, 'links': []}
    
    if max_delay == None: 
        max_delay = 1000

    if max_cap == None:
        max_cap = 100

    for _ in range(l):
        src = random.randint(0, n-1) 
        while(True):
            dst = random.randint(0, n-1)
            if dst != src:
                break
        delay = random.randint(0, max_delay)
        cap = random.randint(0, max_cap)

        link_data = (src, dst, delay, cap )
        topo_dict['links'].append(link_data)
    
    with open(topo_f, 'w') as f:
        f.write(f"{n} {l}\n")
        for link in topo_dict['links']:
            f.write(f"{link[0]} {link[1]} {link[2]} {link[3]}\n")

    conns_dict = {'r': r, 'requests': []}
    for _ in range(r):
        src = random.randint(0, n-1)
        while(True):
            dst = random.randint(0, n-1)
            if dst != src:
                break
        bmin = random.randint(0, max_cap)
        bmax = random.randint(bmin, max_cap)
        bave = random.randint(bmin, bmax)
        request = (src, dst, bmin, bave, bmax)
        conns_dict['requests'].append(request)
    
    with open(conn_f, 'w') as f:
        f.write(f"{r}\n")
        for request in conns_dict['requests']:
            f.write(f"{request[0]} {request[1]} {request[2]} {request[3]} {request[4]}\n")

if __name__ == "__main__":
    # random.seed(0)
    parser = argparse.ArgumentParser(prog="Test cases generator",
                                     description="Generates test cases. Generates ")
    parser.add_argument('-t', help="Topology file", action="store", required=True, type=str)
    parser.add_argument('-c', help="Connections file", action="store", required=True, type=str)
    parser.add_argument('-n', help="No. of node", action="store", required=True, type=int)
    parser.add_argument('-l', help="No. of links", action="store", required=True, type=int)
    parser.add_argument('-delay', help="Max delay on any link", action="store", required=False, type=int)
    parser.add_argument('-cap', help="Max capacity on any link", action="store", required=False, type=int)
    parser.add_argument('-r', help="No. of requests", action="store", required=True, type=int)
    args = parser.parse_args()

    generate_tc(topo_f=args.t, conn_f=args.c, n=args.n, l=args.l, max_delay=args.delay, max_cap=args.cap, r=args.r)