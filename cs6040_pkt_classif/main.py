#!/usr/bin/env python3

import argparse
import graphviz

class TrieNode:
    def __init__(self):
        self.rules = []                 # The rules of the current header that match the prefix. Store rule no. from the input file
        self.children = {}              # Binary Trie, so 2 children
        self.end_node = False

    def __repr__(self, level=0) -> str:
        children_str = ", ".join([f"{key}:{child}" for key, child in self.children.items()])
        return f"{' '*level}Node(Children: {{ {children_str} }}, Rules: {self.rules}, End Node: {self.end_node})"
    
    def add_child(self, bit, child_node):
        self.children[bit] = child_node

class Trie:
    def __init__(self, pfx=None):
        # TODO: Handle case when root is *.
        self.root = TrieNode()          
        if pfx:
            self.add(pfx, rule_num=-1)

    def add(self, pfx, rule_num):
        current = self.root
        for bit in pfx:
            if bit not in current.children.keys():
                current.children[bit] = TrieNode()
            current = current.children[bit]
        # TODO: When does end node become false?
        current.rules.append(rule_num)          # Correct?
        current.end_node = True         

    def __repr__(self) -> str:
        return repr(self.root)
    
    def visualize(self):
        dot = graphviz.Digraph(comment="Trie Visualization")

        def add_edges(node, prefix=""):
            if node.rules:
                dot.node(prefix, label=f"Rules: {node.rules}, End Node: {node.end_node}")
            for bit, child in node.children.items():
                child_prefix = f"{prefix}{bit}"
                dot.node(child_prefix)
                dot.edge(prefix, child_prefix, label=bit)
                add_edges(child, child_prefix)
        
        add_edges(self.root)
        return dot

def ip2binary(addr):
    b1, b2, b3, b4 = map(int, addr.strip().split("."))
    return f"{(b1):08b}{(b2):08b}{(b3):08b}{(b4):08b}"

class Router:
    def __init__(self, rules_f, ip_f) -> None:
        self.rules_table = []
        self.inputs = []
        self.output = []                # Tuple: (addr1, addr2, #matches, #rules matched, search time)
        self.trie_table = Trie()

        with open(rules_f, 'r') as f:
            for i, line in enumerate(f):
                entry1, entry2 = map(str, line.strip().split(" "))
                addr1, pfx_len1 = map(str, entry1.strip().split("/"))
                addr2, pfx_len2 = map(str, entry2.strip().split("/")) 

                self.rules_table.append((i, addr1, int(pfx_len1), addr2, int(pfx_len2)))
        
        with open(ip_f, 'r') as f:
            for line in f:
                addr1, addr2 = map(str, line.strip().split(" "))
                self.inputs.append((addr1, addr2))
       
       # TODO: Build trie
        self.__construct_hierarchial_trie()

        dot = self.trie_table.visualize()
        dot.render("TG", view=True)

        print(repr(self.trie_table))
        
    def __construct_hierarchial_trie(self):
        for entry in self.rules_table:
            rule_num, addr1, pfx_len1, addr2, pfx_len2 = entry
            
            #TODO: Add in level 1
            addr1 = ip2binary(addr=addr1)
            self.trie_table.add(addr1[pfx_len1], rule_num=rule_num)

            #TODO: Add in level 2
            # addr2 = ip2binary(addr=addr2)

    def run(self):
        pass

    def print_out(self, outf):
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Rules file", type=str, )
    parser.add_argument("-i", help="Input Address file", type=str)
    parser.add_argument("-o", help="Output file", type=str)
    
    args = parser.parse_args()
    
    router = Router(args.p, args.i)
    router.run()
    router.print_out(args.o)
