#!/usr/bin/python3

import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import copy

class Router:
    def __init__(self) -> None:
        pass

class Exercise:
    def __init__(self, topo_file=None, conn_file=None, rt_file=None, ft_file=None, path_file=None, flag=None, p=None) -> None:
        self.topo_file = topo_file
        self.conn_file = conn_file
        self.rt_file = rt_file
        self.ft_file = ft_file
        self.path_file = path_file
        self.flag = flag
        self.p = p

        self.routes_matrix = None
        self.nw = nx.Graph()
        
    def run(self) -> None:
        self.build_network()
        self.build_routing_table()
        self.process_connections()

    def build_network(self) -> None:
        with open(self.topo_file) as f:
            num_nodes, num_edges = map(int, f.readline().split())
            self.nw.add_nodes_from(range(num_nodes))
            for edge in range(num_edges):
                node1, node2, prop_delay, edge_cap = map(int, f.readline().split())
                self.nw.add_edge(node1, node2, delay=prop_delay, cap=edge_cap)
        
        # pos = nx.spring_layout(self.nw)
        # nx.draw(self.nw, pos, with_labels=True)
        # edge_labels = {(u, v): f"[{d['delay']}, {d['cap']}]" for u, v, d in self.nw.edges(data=True)}
        # nx.draw_networkx_edge_labels(self.nw, pos, edge_labels=edge_labels, font_color='red')
        # plt.savefig("topo.png")
        # plt.show(block=False)
        # plt.pause(1)
        # plt.show()
    
    def build_routing_table(self) -> None:
        open(self.rt_file, 'w').close()
        for node in self.nw.nodes:
            paths = self.get_paths(src_node=node)
            with open(self.rt_file, 'a') as f:
                f.write(f"--X-- Routing table for Node: {node} --X--\n")
                for dst_node in paths.keys():
                    f.write(f"{dst_node} {str(paths[dst_node][0]['path'])}  {paths[dst_node][0]['delay']} {paths[dst_node][0]['cost']} \n")
                    f.write(f"{dst_node} {str(paths[dst_node][1]['path'])}  {paths[dst_node][1]['delay']} {paths[dst_node][1]['cost']} \n")
                f.write("\n\n")

    
    def process_connections(self) -> None:
        pass

    def get_paths(self, src_node=None) -> dict:
        # Add number of paths to generalize
        paths = {node: [{'path': [], 'delay': 0, 'cost': 0}, {'path': [], 'delay': 0, 'cost': 0}] for node in self.nw.nodes}
        """
        OPTIMIZATION: Run Floyd-Warshall/Dijkstra here to get 1st level, single source shortest paths for src_node.
        """

        for node in self.nw.nodes:
            nw_copy = nx.DiGraph()
            for u, v, weights in self.nw.edges(data=True):
                nw_copy.add_edge(u, v, delay=weights['delay'], cap=weights['cap'])
                nw_copy.add_edge(v, u, delay=weights['delay'], cap=weights['cap'])

            # Suurballe's algorithm
            # path1 = self.get_shortest_path(nw_copy, src_node=src_node, dst_node=node)
            # self.modify_network(nw_copy)
            # path2 = self.get_shortest_path(nw_copy, src_node=src_node, dst_node=node)
            
            # Yen's algorithm
            path1, path2 = self.yenKSP(nw=nw_copy, src=src_node, dst=node, K=2)

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
        paths = [[]] * K
        lens = [-1] * K
        if self.flag == "hop":
            if src == dst:
                return [src, dst], [src, dst] 
            
            lens[0], paths[0] = nx.single_source_dijkstra(nw, src, dst)
            # print(f"s: {src}, d: {dst}, len: {len1}, path: {path1}")
            B = []

            for k in range(1, K):
                for i in range(0, len(paths[-1])-1):
                    spur_node = paths[-1][i]
                    root_path = paths[-1][0: i+1]

                    for p in paths:
                        if len(p) > i and root_path == p[0: i+1]:
                            u = p[i]
                            v = p[i]
                            if nw.has_edge(u, v):
                                nw.remove_edge(u, v)
                    
                    for n in range(len(root_path) - 1):
                        node = root_path[n]
                        for u, v in nw.edges(node):
                            nw.remove_edge(u, v)
                            nw.remove_edge(v, u)
                        
                        if nw.is_directed():
                            for u, v in nw.in_edges:
                                pass
                    

        if self.flag == "dist":
            pass

        # A = [[]] * K    # shortest paths
        # B = []          # potential kth shortest path
        
        # # First shortest path from src to dst
        # A[0] = self.dijkstras(nw=nw, src_node=src, dst_node=dst)

        # for k in range(1, K):
        #     for i in range(0, len(A[k-1]) - 2):
        #         pass

        # return A[0], A[1]
        return None, None

    def dijkstras(self, nw=None, src_node=None, dst_node=None) -> None:
        # dijkstra's
        dist = []
        path = []
        num_nodes = len(nw.nodes())
        visited_nodes = {src_node: 0}
        nodes = list(nw.nodes())


        return path

    def modify_network(self, nw) -> None:
        pass

    def calculate_delay(self, path) -> None:
        delay = 0
        return delay

    def calculate_cost(self, path) -> None:
        cost = 0
        return cost


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
    
    exercise = Exercise(topo_file=args.top, conn_file=args.conn, rt_file=args.rt, ft_file=args.ft, path_file=args.path, flag=args.flag, p=args.p)
    exercise.run()
    # exercise.run_connection_requests()