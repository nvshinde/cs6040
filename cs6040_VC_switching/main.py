#!/usr/bin/python3

import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from itertools import count
import heapq
import copy
import pprint

class Router:
    def __init__(self) -> None:
        pass

class Exercise:
    def __init__(self, topo_file=None, conn_file=None, rt_file=None, ft_file=None, path_file=None, flag=None, approach=None) -> None:
        self.topo_file = topo_file
        self.conn_file = conn_file
        self.rt_file = rt_file
        self.ft_file = ft_file
        self.path_file = path_file
        self.flag = flag
        self.approach = approach

        self.nw = nx.Graph()
        self.routing_table = {}
        self.forwarding_table = {} # {node: {conn: {nid_in, vcid_in, nid_out, vcid_out}}}
        self.paths_table = {} # {conn: {src, dst, path, vcid list, pathcost}}
        self.connection_requests = {}

    def run(self) -> None:
        # Build network
        with open(self.topo_file) as f:
            num_nodes, num_edges = map(int, f.readline().split())
            self.nw.add_nodes_from(range(num_nodes))
            for edge in range(num_edges):
                node1, node2, prop_delay, edge_cap = map(int, f.readline().split())
                self.nw.add_edge(node1, node2, delay=prop_delay, cap=edge_cap, conns=[])
        
        # Get network image
        # pos = nx.spring_layout(self.nw)
        # nx.draw(self.nw, pos, with_labels=True)
        # edge_labels = {(u, v): f"[{d['delay']}, {d['cap']}]" for u, v, d in self.nw.edges(data=True)}
        # nx.draw_networkx_edge_labels(self.nw, pos, edge_labels=edge_labels, font_color='red')
        # plt.savefig("topo.png")
        # plt.show(block=False)
        # plt.pause(1)
        # plt.show()

        self.build_routing_table()
        
        # Read connection requests
        with open(self.conn_file, 'r') as f:
            num_connections = int(f.readline().strip())
            for i in range(num_connections):
                src, dst, bmin, bave, bmax = map(int, f.readline().split())
                # print(src, dst, bmin, bave, bmax)
                self.connection_requests[i] = {'src': src, 
                                               'dst': dst, 
                                               'bmin': bmin, 
                                               'bave': bave, 
                                               'bmax': bmax}
        
        # pprint.pprint(self.connection_requests)

        self.process_connections()
        print(self.nw.edges(data=True))
    
    def build_routing_table(self) -> None:
        open(self.rt_file, 'w').close()
        for node in self.nw.nodes:
            paths = self.get_paths(src_node=node)
            with open(self.rt_file, 'a') as f:
                f.write(f"--X-- Routing table for Node: {node} --X--\n")
                self.routing_table[node] = {}
                for dst_node in paths.keys():
                    f.write(f"{dst_node} {str(paths[dst_node][0]['path'])}  {paths[dst_node][0]['delay']} {paths[dst_node][0]['cost']} \n")
                    f.write(f"{dst_node} {str(paths[dst_node][1]['path'])}  {paths[dst_node][1]['delay']} {paths[dst_node][1]['cost']} \n")
                    self.routing_table[node][dst_node] = {
                                                            'path1': {
                                                                'path': paths[dst_node][0]['path'], 
                                                                'delay': paths[dst_node][0]['delay'], 
                                                                'cost': paths[dst_node][0]['cost']
                                                            }, 
                                                            'path2': {
                                                                'path': paths[dst_node][1]['path'], 
                                                                'delay': paths[dst_node][1]['delay'], 
                                                                'cost': paths[dst_node][1]['cost']
                                                            }
                                                        }
                f.write("\n\n")
        # pprint.pprint(self.routing_table)

    def get_paths(self, src_node=None) -> dict:
        # Add number of paths to generalize
        paths = {node: [{'path': [], 'delay': 0, 'cost': 0}, {'path': [], 'delay': 0, 'cost': 0}] for node in self.nw.nodes}
        """
        OPTIMIZATION: Run Floyd-Warshall/Dijkstra here to get 1st level, single source shortest paths for src_node.
        """

        for node in self.nw.nodes:
            nw_copy = copy.deepcopy(self.nw)
            
            # Yen's algorithm
            path1, path2 = self.yenKSP(nw=nw_copy, src=src_node, dst=node, K=2)

            if path1 == None:
                paths[node][0]['path'] = [node]
                paths[node][1]['path'] = [node]

                paths[node][0]['delay'] = 0
                paths[node][1]['delay'] = 0

                paths[node][0]['cost'] = 0
                paths[node][1]['cost'] = 0
            else:
                paths[node][0]['path'] = path1
                paths[node][1]['path'] = path2

                paths[node][0]['delay'] = self.calculate_delay(path1)
                paths[node][1]['delay'] = self.calculate_delay(path2)

                paths[node][0]['cost'] = self.calculate_cost(path1)
                paths[node][1]['cost'] = self.calculate_cost(path2)
        return paths

    def yenKSP(self, nw, src, dst, K=1):
        """
        K hardcoded now
        """
        paths = []
        lens = []
        counter = count()
        potential_paths = []

        if src == dst:
            return None, None
         
        if self.flag == "hop":
            l, p = nx.single_source_dijkstra(nw, src, dst)
        
        if self.flag == "dist":
            l, p = nx.single_source_dijkstra(nw, src, dst, weight='delay')
        
        paths.append(p)
        lens.append(l)
    
        # print(f"s: {src}, d: {dst}, len: {l}, path: {p}")

        for k in range(1, K):
            for i in range(0, len(paths[-1])-1):
                root_path = paths[-1][0 : i+1]
                spur_node = paths[-1][i]


                for p in paths:
                    if len(p) > i and root_path == p[0 : i+1]:
                        if nw.has_edge(p[i], p[i+1]):
                            nw.remove_edge(p[i], p[i+1])
                
                for n in range(len(root_path) - 1):
                    node = root_path[n]
                    for u, v in list(nw.edges(node)):
                        nw.remove_edge(u, v)
                # print(f"src:{src}, dst:{dst}, k:{k}, i:{i}, edges:{nw.edges()}")
                if self.flag == "hop":    
                    try:
                        spur_path_len, spur_path = nx.single_source_dijkstra(nw, spur_node, dst)
                    except:
                        continue

                if self.flag == "dist":    
                    try:
                        spur_path_len, spur_path = nx.single_source_dijkstra(nw, spur_node, dst, weight='delay')
                    except:
                        continue

                if dst in spur_path:
                    total_path = root_path[:-1] + spur_path
                    total_path_len = self.get_path_len(root_path) + spur_path_len
                    heapq.heappush(potential_paths, (total_path_len, next(counter), total_path))
        # print(potential_paths)
        if potential_paths:
            l, _, p = heapq.heappop(potential_paths)
            lens.append(l)
            paths.append(p)

        return paths[0], paths[1]
    
    def get_path_len(self, path):
        length = 0
        if self.flag == "hop":
            if len(path) > 1:
                for i in range(len(path) - 1):
                    length += 1
        if self.flag == "dist":
            if len(path) > 1:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    length += self.nw.get_edge_data(u, v, default={'delay': 0, 'cap': 0})['delay']
        return length

    def calculate_delay(self, path) -> None:
        # print("path", path)
        delay = 0
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            # print("del:", self.nw.get_edge_data(u, v, default=0))
            delay += self.nw.get_edge_data(u, v, default={'delay': 0, 'cap': 0})['delay']
        return delay

    def calculate_cost(self, path) -> None:
        cost = 0
        if self.flag == "hop":
            cost = len(path) - 1 
        if self.flag == "dist":
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                cost += self.nw.get_edge_data(u, v, default={'delay': 0, 'cap': 0})['delay']  
        return cost
        
    def process_connections(self) -> None:
        if self.approach == 0: # optimistic approach
            for conn_i, conn_i_data in self.connection_requests.items():
                # print(conn_id, connection)
                path1_conn_i = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path1']['path']
                path2_conn_i = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path2']['path']
                
                print(conn_i, path1_conn_i, path2_conn_i)
                
                conn_i_admit = True
                conn_i_admit_path = None

                beqv_i = min(conn_i_data['bmax'], conn_i_data['bave'] + 0.35 * (conn_i_data['bmax'] - conn_i_data['bmin']))
                for i in range(len(path1_conn_i)-1):
                    u, v = path1_conn_i[i], path1_conn_i[i+1]
                    c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                    sum_beqv_j = 0
                    for conn_j in link_conns:
                        sum_beqv_j += min(self.connection_requests[conn_j]['bmax'], 
                                          self.connection_requests[conn_j]['bave'] + 0.35 * (self.connection_requests[conn_j]['bmax'] - self.connection_requests[conn_j]['bmin']))
                    
                    if beqv_i > (c_l - sum_beqv_j):
                        conn_i_admit = False
                        break
                
                if conn_i_admit:
                    print(f"{conn_i} admitted on path1")
                    conn_i_admit_path = path1_conn_i
                    for i in range(len(path1_conn_i) - 1):
                        u, v = path1_conn_i[i], path1_conn_i[i+1]
                        edge_data = self.nw.get_edge_data(u, v)
                        edge_data['conns'].append(conn_i)
                else:
                    print(f"{conn_i} not admitted on path1. Trying path2")
                    conn_i_admit = True
                    for i in range(len(path2_conn_i)-1):
                        u, v = path2_conn_i[i], path2_conn_i[i+1]
                        c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                        sum_beqv_j = 0
                        for conn_j in link_conns:
                            sum_beqv_j += min(self.connection_requests[conn_j]['bmax'],
                                              self.connection_requests[conn_j]['bave'] + 0.35 * (self.connection_requests[conn_j]['bamx'] - self.connection_requests[conn_j]['bmin']))
                        
                        if beqv_i > (c_l - sum_beqv_j):
                            conn_i_admit = False
                            break
                
                    if conn_i_admit:
                        print(f"{conn_i} admitted on path2")
                        conn_i_admit_path = path2_conn_i
                        for i in range(len(path2_conn_i) - 1):
                            u, v = path2_conn_i[i], path2_conn_i[i+1]
                            edge_data = self.nw.get_edge_data(u, v)
                            edge_data['conns'].append(conn_i)

                if not conn_i_admit:
                    print(f"{conn_i} not admitted on any path")
                else:
                    """setup the connection vcids"""

                    pass

                # print(self.nw.edges(data=True))

        elif self.approach == 1: # pessimistic approach
            pass
            for conn_i, conn_i_data in self.connection_requests.items():
                # print(conn_id, connection)
                path1_conn_i = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path1']['path']
                path2_conn_i = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path2']['path']
                
                print(conn_i, path1_conn_i, path2_conn_i)
                
                conn_i_admit = True
                conn_i_admit_path = None

                # beqv_i = min(conn_i_data['bmax'], conn_i_data['bave'] + 0.35 * (conn_i_data['bmax'] - conn_i_data['bmin']))
                for i in range(len(path1_conn_i)-1):
                    u, v = path1_conn_i[i], path1_conn_i[i+1]
                    c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                    sum_bmax_j = 0
                    for conn_j in link_conns:
                        sum_bmax_j += self.connection_requests[conn_j]['bmax']
                    
                    if self.connection_requests[conn_i]['bmax'] > (c_l - sum_bmax_j):
                        conn_i_admit = False
                        break
                
                if conn_i_admit:
                    print(f"{conn_i} admitted on path1")
                    conn_i_admit_path = path1_conn_i
                    for i in range(len(path1_conn_i) - 1):
                        u, v = path1_conn_i[i], path1_conn_i[i+1]
                        edge_data = self.nw.get_edge_data(u, v)
                        edge_data['conns'].append(conn_i)
                else:
                    print(f"{conn_i} not admitted on path1. Trying path2")
                    conn_i_admit = True
                    for i in range(len(path2_conn_i)-1):
                        u, v = path2_conn_i[i], path2_conn_i[i+1]
                        c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                        sum_bmax_j = 0
                        for conn_j in link_conns:
                            sum_bmax_j += self.connection_requests[conn_j]['bmax']
                        
                        if self.connection_requests[conn_i]['bmax'] > (c_l - sum_bmax_j):
                            conn_i_admit = False
                            break
                
                    if conn_i_admit:
                        print(f"{conn_i} admitted on path2")
                        conn_i_admit_path = path2_conn_i
                        for i in range(len(path2_conn_i) - 1):
                            u, v = path2_conn_i[i], path2_conn_i[i+1]
                            edge_data = self.nw.get_edge_data(u, v)
                            edge_data['conns'].append(conn_i)

                if not conn_i_admit:
                    print(f"{conn_i} not admitted on any path")
                else:
                    """setup the connection vcids"""
                    pass

                # print(self.nw.edges(data=True)) 
        
        else:
            print("Approach flag 'p' is incorrect. Specify {0, 1}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog="Virtual Circuit Switching", 
                                     description="Simulates VC switching")
    
    parser.add_argument('-top', help="Topology File", action="store", required=True, type=str)
    parser.add_argument('-conn', help="Connections File", action="store", required=True, type=str)
    parser.add_argument('-rt', help="Routing Table File", action="store", required=True, type=str)
    parser.add_argument('-ft', help="Forwarding File", action="store", required=True, type=str)
    parser.add_argument('-path', help="Paths File", action="store", required=True, type=str)
    parser.add_argument('-flag', help="Flag for shortest cost path", action="store", required=True, default="hop", type=str)
    parser.add_argument('-p', help="Approach: Optimistic of Pessimistic", required=True, default=0, type=int)
    
    args = parser.parse_args()

    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'outputs')
    log_dir = os.path.join(cwd, 'logs')
    
    exercise = Exercise(topo_file=args.top, conn_file=args.conn, rt_file=args.rt, ft_file=args.ft, path_file=args.path, flag=args.flag, approach=args.p)
    exercise.run()
    # exercise.run_connection_requests()