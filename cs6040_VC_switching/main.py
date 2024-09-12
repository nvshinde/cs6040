
import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from itertools import count
import heapq
import copy
import pprint
import random
import logging

# TODO:
# Add error handling 
# Cannot handle if no second path is found

class Exercise:
    def __init__(self, topo_file=None, conn_file=None, rt_file=None, ft_file=None, path_file=None, flag=None, approach=None) -> None:
        """
        Initialize object variables.
        """
        logging.info("Created exercise object")
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
        self.failed_connections = {'n': 0, 'conns': []}
            

    def run(self) -> None:
        """
        Runs the lab. 
        """
        logging.info("Starting Exercise")

        if os.path.isfile(self.topo_file):
            # Parse topology file and build network
            with open(self.topo_file, 'r') as f:
                num_nodes, num_edges = map(int, f.readline().split())
                self.nw.add_nodes_from(range(num_nodes))
                for edge in range(num_edges):
                    node1, node2, prop_delay, edge_cap = map(int, f.readline().split())
                    self.nw.add_edge(node1, node2, delay=prop_delay, cap=edge_cap, conns=[])
            logging.debug(f"Network edges: {self.nw.edges(data=True)}")
        else:
            logging.error("Topology file does not exist")
            print("-----------Check log file-----------")
            exit(1)
    
        self.forwarding_table = {node: {} for node in range(num_nodes)}
        
        # Ouput a network image with attributes
        """
        pos = nx.spring_layout(self.nw)
        nx.draw(self.nw, pos, with_labels=True)
        edge_labels = {(u, v): f"[{d['delay']}, {d['cap']}]" for u, v, d in self.nw.edges(data=True)}
        nx.draw_networkx_edge_labels(self.nw, pos, edge_labels=edge_labels, font_color='red')
        plt.savefig("topo.png")
        plt.show(block=False)
        plt.pause(1)
        plt.show()
        """

        self.build_routing_table()
        
        if os.path.isfile(self.conn_file):
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
            logging.debug(f"Connection requests: {self.connection_requests}")
        else:
            logging.error("Connection file does not exist")
            print("-----------Check log file-----------")
            exit(1)
        
        self.process_connections()

        # Write to forwarding file
        with open(self.ft_file, 'w') as f:
            f.write(f"Router ID, NID_IN, VCID_IN, NID_OUT, VCID_OUT\n")
            for node, conns in self.forwarding_table.items():
                if conns:
                    for conn, data in conns.items():
                        f.write(f"{node}, {data['nid_in']}, {data['vcid_in']}, {data['nid_out']}, {data['vcid_out']}\n")
                else:
                    f.write(f"{node}, -, -, -, -\n")
        logging.debug(f"Forwarding table: {self.forwarding_table}")

        # Write to paths file
        with open(self.path_file, 'w') as f:
            f.write(f"CONN ID, SOURCE, DST, PATH, VCIDs, PATH COST\n")
            for conn, data in self.paths_table.items():
                f.write(f"{conn}, {data['src']}, {data['dst']}, {data['path']}, {data['vcids']}, {data['cost']}\n")
        logging.debug(f"Paths table: {self.paths_table}")

        logging.info(f"Failed connections: {self.failed_connections}")

        print(f"No. of requests: {len(self.connection_requests)}\n\
No. of blocked requests: {self.failed_connections['n']}\n\
Blocking probability: {self.failed_connections['n'] / len(self.connection_requests)}")
        
        logging.info(f"Exercise Finished")

    def build_routing_table(self) -> None:
        """
        Builds a routing table with 2 shortest paths for all pairs
        """
        logging.info("Building Routing table")
        
        open(self.rt_file, 'w').close()

        for node in self.nw.nodes:
            paths = self.get_paths(src_node=node)
            with open(self.rt_file, 'a') as f:
                f.write(f"--X-- Routing table for Node: {node} --X--\n")
                f.write(f"DST, PATH, DELAY, COST\n")
                self.routing_table[node] = {}
                for dst_node in paths.keys():
                    f.write(f"{dst_node}, {str(paths[dst_node][0]['path'])}, {paths[dst_node][0]['delay']}, {paths[dst_node][0]['cost']} \n")
                    f.write(f"{dst_node}, {str(paths[dst_node][1]['path'])}, {paths[dst_node][1]['delay']}, {paths[dst_node][1]['cost']} \n")
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
        logging.debug(f"Routing Table: {self.routing_table}")
        # pprint.pprint(self.routing_table)

    def get_paths(self, src_node=None) -> dict:
        """
        Return paths from src node to all other nodes. 
        Returns paths with single node for src to src.

        Only returns 2 paths for each destination from src node.

        TODO: 
            Add number of paths to generalize.
            OPTIMIZATION: Run Floyd-Warshall/Dijkstra here to get 1st level, single source shortest paths for src_node.
        """
        logging.debug(f"Getting paths for src: {src_node}")
        paths = {node: [{'path': [], 'delay': 0, 'cost': 0}, {'path': [], 'delay': 0, 'cost': 0}] for node in self.nw.nodes}

        for node in self.nw.nodes:
            nw_copy = copy.deepcopy(self.nw)
            
            # Yen's algorithm
# BUG: A graph having no path between src and dst returns None.
            path1, path2 = self.yenKSP(nw=nw_copy, src=src_node, dst=node, K=2)

# BUG: Handle src == dst differently
            if path1 != [-1] and path2 == [-1]:
                path2 = path1

            if path1 == path2:
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
        logging.debug(f"Path to all dst: {paths}")
        return paths

    def yenKSP(self, nw, src, dst, K=2):
        """
        Runs Yen's algorithm to find top 2 shortest paths. 
        The paths are not necessarily link disjoint.

        Returns:
        Tuple containing two lists of shortest paths 
        
        TODO:
            Generalize according to K. K hardcoded now. 
        """
        paths = [] # shortest paths
        lens = [] # lenghts of shortest paths
        counter = count() # iterator for priority queue
        potential_paths = []

        if src == dst:
            return [src], [src]

# BUG: Handle if path not found        
        # Get first shortest path        
        try:
            if self.flag == "hop":
                l, p = nx.single_source_dijkstra(nw, src, dst)
            if self.flag == "dist":
                l, p = nx.single_source_dijkstra(nw, src, dst, weight='delay')            
        except:
            return [-1], [-1]
        
        paths.append(p)
        lens.append(l)
    
        # Get second non link disjoint shortest path
        # """
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

# BUG: Handle if 2nd path not found
                try:
                    if self.flag == "hop":    
                        spur_path_len, spur_path = nx.single_source_dijkstra(nw, spur_node, dst)
                    if self.flag == "dist":    
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
        # """        
        
        """
        # Get second link disjoint shortest path
        path1_edges = [(paths[0][i], paths[0][i+1]) for i in range(len(paths[0]) - 1)]
        nw.remove_edges_from(path1_edges)
        try:
            if self.flag == "hop":
                tmp_len, tmp_path = nx.single_source_dijkstra(nw, src, dst)
            if self.flag == "dist":
                tmp_len, tmp_path = nx.single_source_dijkstra(nw, src, dst, weight='delay')
        except:
            tmp_path = [-1]
        
        paths.append(tmp_path)
        """
# BUG: Handle empty returns
        return paths[0], paths[1]
    
    def get_path_len(self, path) -> int:
        """
        Get path length
        Input: path
        Returns: int length
        """
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
        """
        Get path delay
        Input: path
        Returns: int delay
        """
        delay = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            delay += self.nw.get_edge_data(u, v, default={'delay': 0, 'cap': 0})['delay']
        return delay

    def calculate_cost(self, path) -> None:
        """
        Calculate cost. Similar to get_path_len()
        Input: path
        Returns: int cost based on hop or dist defined.
        """
        cost = 0
        if self.flag == "hop":
            cost = len(path) - 1 
        if self.flag == "dist":
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                cost += self.nw.get_edge_data(u, v, default={'delay': 0, 'cap': 0})['delay']  
        return cost
        
    def process_connections(self) -> None:
        for conn_i, conn_i_data in self.connection_requests.items():
            # print(conn_i, conn_i_data)
            conn_i_path1 = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path1']['path']
            conn_i_path2 = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path2']['path']
            # print(conn_i, conn_i_path1, conn_i_path2)
            
            if len(conn_i_path1) > 1:
                conn_i_admit = True
                conn_i_admit_path = None

                if self.approach == 0:
                    beqv_i = min(conn_i_data['bmax'], conn_i_data['bave'] + 0.35 * (conn_i_data['bmax'] - conn_i_data['bmin']))

                for i in range(len(conn_i_path1)-1):
                    u, v = conn_i_path1[i], conn_i_path1[i+1]
                    c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                    if self.approach == 0:
                        sum_beqv_j = 0
                        for conn_j in link_conns:
                            sum_beqv_j += min(self.connection_requests[conn_j]['bmax'], 
                                            self.connection_requests[conn_j]['bave'] + 0.35 * (self.connection_requests[conn_j]['bmax'] - self.connection_requests[conn_j]['bmin']))
                        
                        if beqv_i > (c_l - sum_beqv_j):
                            conn_i_admit = False
                            break
                    if self.approach == 1:
                        sum_bmax_j = 0
                        for conn_j in link_conns:
                            sum_bmax_j += self.connection_requests[conn_j]['bmax']
                        
                        if self.connection_requests[conn_i]['bmax'] > (c_l - sum_bmax_j):
                            conn_i_admit = False
                            break
                if conn_i_admit:
                    logging.debug(f"Connection {conn_i} admitted on path1: {conn_i_path1}")
                    conn_i_admit_path = conn_i_path1
                    for i in range(len(conn_i_path1) - 1):
                        u, v = conn_i_path1[i], conn_i_path1[i+1]
                        edge_data = self.nw.get_edge_data(u, v)
                        edge_data['conns'].append(conn_i)
                else:
                    logging.debug(f"Connection {conn_i} not admitted on path1. Trying path2")
                    conn_i_admit = True
                    for i in range(len(conn_i_path2)-1):
                        u, v = conn_i_path2[i], conn_i_path2[i+1]
                        c_l, link_conns = self.nw.get_edge_data(u, v)['cap'], self.nw.get_edge_data(u, v)['conns']
                        
                        if self.approach == 0:
                            sum_beqv_j = 0
                            for conn_j in link_conns:
                                    sum_beqv_j += min(self.connection_requests[conn_j]['bmax'],
                                                self.connection_requests[conn_j]['bave'] + 0.35 * (self.connection_requests[conn_j]['bmax'] - self.connection_requests[conn_j]['bmin']))
                            if beqv_i > (c_l - sum_beqv_j):
                                conn_i_admit = False
                                break

                        if self.approach == 1:
                            sum_bmax_j = 0
                            for conn_j in link_conns:
                                sum_bmax_j += self.connection_requests[conn_j]['bmax']
                            if self.connection_requests[conn_i]['bmax'] > (c_l - sum_bmax_j):
                                conn_i_admit = False
                                break
                
                    if conn_i_admit:
                        logging.debug(f"{conn_i} admitted on path2: {conn_i_path2}")
                        conn_i_admit_path = conn_i_path2
                        for i in range(len(conn_i_path2) - 1):
                            u, v = conn_i_path2[i], conn_i_path2[i+1]
                            edge_data = self.nw.get_edge_data(u, v)
                            edge_data['conns'].append(conn_i)

                if not conn_i_admit:
                    logging.debug(f"{conn_i} not admitted on any path")
                    self.failed_connections['n'] = self.failed_connections['n'] + 1
                    self.failed_connections['conns'].append(conn_i)
                else:
                    """setup the connection vcids"""

                    conn_i_vcids = {} # {node: {vcid_in, vcid_out}}
                    vcid_list = []

                    for i, node in enumerate(conn_i_admit_path):
                        # skip src and dst
                        if i == 0:
                            # src node only has vcid_out
                            vcid_out = self.get_new_vcid(node=node, flag="out")
                            conn_i_vcids[node] = {'vcid_in': -1, 'vcid_out': vcid_out}
                            self.forwarding_table[node][conn_i] = {'nid_in': -1, 
                                                                    'vcid_in': -1, 
                                                                    'nid_out': conn_i_admit_path[i+1],
                                                                    'vcid_out': vcid_out}
                            vcid_list.append(vcid_out)
                        elif i == len(conn_i_admit_path) - 1:
                            # dst node only has vcid_in
                            vcid_in = conn_i_vcids[conn_i_admit_path[i-1]]['vcid_out']
                            conn_i_vcids[node] =  {'vcid_in': vcid_in, 'vcid_out': -1}
                            self.forwarding_table[node][conn_i] = {'nid_in': conn_i_admit_path[i-1], 
                                                                    'vcid_in': vcid_in, 
                                                                    'nid_out': -1,
                                                                    'vcid_out': -1}
                        else:
                            # for all other nodes                         
                            vcid_in = conn_i_vcids[conn_i_admit_path[i-1]]['vcid_out']
                            vcid_out = self.get_new_vcid(node=node, flag="out")

                            conn_i_vcids[node] = {'vcid_in': vcid_in, 'vcid_out': vcid_out}
                            self.forwarding_table[node][conn_i] = {'nid_in': conn_i_admit_path[i-1], 
                                                                    'vcid_in': vcid_in, 
                                                                    'nid_out': conn_i_admit_path[i+1],
                                                                    'vcid_out': vcid_out}
                    
                            vcid_list.append(vcid_out)

                    if conn_i_admit_path in self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path1'].values():
                        cost = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path1']['cost']
                    else:
                        cost = self.routing_table[conn_i_data['src']][conn_i_data['dst']]['path2']['cost']

                    self.paths_table[conn_i] = {
                                                'src': conn_i_data['src'],
                                                'dst': conn_i_data['dst'],
                                                'path': conn_i_admit_path,
                                                'vcids': vcid_list,
                                                'cost': cost
                                                }

            # print(self.nw.edges(data=True))

    def get_new_vcid(self, node, flag) -> list:
        """
        Get vcid for the node.
        Input: 
            node, flag ("in", "out")
        Returns: Vcid list
        """
        vcid = random.randint(0, self.nw.number_of_nodes())
        if node not in self.forwarding_table.keys():
            return vcid
        
        if flag == "in":
            for conn, _ in self.forwarding_table[node].items():
                if vcid == self.forwarding_table[node][conn]['vcid_in']:
                    vcid = random.randint(0, self.nw.number_of_nodes())
                else:
                    continue
    
        if flag == "out":
            for conn, _ in self.forwarding_table[node].items():
                if vcid == self.forwarding_table[node][conn]['vcid_out']:
                    vcid = random.randint(0, self.nw.number_of_nodes())
                else:
                    continue
        
        return vcid

if __name__ == "__main__":

    random.seed(0)
    
    # Logging
    logging.basicConfig(level=logging.DEBUG, filename="log.txt", filemode='w', format="[%(asctime)s] [%(levelname)s]:\n\t %(message)s")

    parser = argparse.ArgumentParser(prog="Virtual Circuit Switching", 
                                     description="Simulates VC switching")
    
    parser.add_argument('-top', help="Topology File", action="store", required=True, type=str)
    parser.add_argument('-conn', help="Connections File", action="store", required=True, type=str)
    parser.add_argument('-rt', help="Routing Table File", action="store", required=True, type=str)
    parser.add_argument('-ft', help="Forwarding File", action="store", required=True, type=str)
    parser.add_argument('-path', help="Paths File", action="store", required=True, type=str)
    parser.add_argument('-flag', help="Flag for shortest cost path", action="store", required=True, default="hop", type=str)
    parser.add_argument('-p', help="Approach: Optimistic(0) of Pessimistic(1)", action="store", required=True, default=0, type=int)
    
    args = parser.parse_args()

    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'outputs')
    log_dir = os.path.join(cwd, 'logs')
    
    exercise = Exercise(topo_file=args.top, conn_file=args.conn, rt_file=args.rt, ft_file=args.ft, path_file=args.path, flag=args.flag, approach=args.p)
    exercise.run()