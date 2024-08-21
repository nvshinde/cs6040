#!/usr/bin/python3

# TODO: 
# 1. Sometimes generates self loops. Remoe

import argparse
import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_tc(max_delay, max_cap, topo_f, conn_f, n, l, r):
    # Generate topology.
    nw = nx.Graph()
    nw.add_nodes_from([node for node in range(n)])

    for _ in range(l):
        src = random.randint(0, n-1) 
        while(True):
            dst = random.randint(0, n-1)
            if dst != src:
                break
        delay = random.randint(0, max_delay)
        cap = random.randint(0, max_cap)
        nw.add_edge(src, dst, delay=delay, cap=cap )
    
    isolated_nodes = list(nx.isolates(nw))
    for node in isolated_nodes:
        dst = random.randint(0, n-1)
        delay = random.randint(0, max_delay)
        cap = random.randint(0, max_cap)
        nw.add_edge(node, dst, delay=delay, cap=cap)
    
    while nx.number_connected_components(nw) != 1:
        all_nodes = set(range(n))
        connected_nodes = set(nx.node_connected_component(nw, random.randint(0, n-1)))
        other_nodes = all_nodes - connected_nodes
        node = list(other_nodes)[-1]
        dst = random.choice(list(connected_nodes))
        delay = random.randint(0, max_delay)
        cap = random.randint(0, max_cap)
        nw.add_edge(node, dst, delay=delay, cap=cap)

    pos = nx.spring_layout(nw)
    nx.draw(nw, pos, with_labels=True)
    edge_labels = {(u, v): f"d: {d['delay']}, c: {d['cap']}" for u, v, d in nw.edges(data=True)}
    nx.draw_networkx_edge_labels(nw, pos, edge_labels=edge_labels, font_color='red')
    plt.savefig("topo.png")
    plt.show()
    
    with open(topo_f, 'w') as f:
        f.write(f"{n} {l}\n")
        for src, dst, data in nw.edges(data=True):
            f.write(f"{src} {dst} {data['delay']} {data['cap']}\n")

    conns_dict = {'r': r, 'requests': []}
    for _ in range(r):
        src = random.randint(0, n-1)
        while(True):
            dst = random.randint(0, n-1)
            if dst != src:
                break
        bmin = random.randint(0, cap)
        bmax = random.randint(bmin, cap)
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
    parser.add_argument('-t', help="O/p Topology file", action="store", type=str, default="topo.txt")
    parser.add_argument('-c', help="O/p Connections file", action="store", type=str, default="conn.txt")
    parser.add_argument('-n', help="No. of node", action="store", type=int, default=random.randint(5, 20))
    parser.add_argument('-l', help="No. of links", action="store", type=int, default=(random.randint(4, 25)))
    parser.add_argument('-delay', help="Max delay on any link", action="store", type=int, default=500)
    parser.add_argument('-cap', help="Max capacity on any link", action="store", type=int, default=100)
    parser.add_argument('-r', help="No. of requests", action="store", type=int, default=random.randint(0, 1000))
    args = parser.parse_args()

    generate_tc(topo_f=args.t, conn_f=args.c, n=args.n, l=args.l, max_delay=args.delay, max_cap=args.cap, r=args.r)