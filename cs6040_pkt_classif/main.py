#!/usr/bin/env python3

import argparse
import graphviz
import time

class TrieNode:
    def __init__(self):
        self.rules = []                                                                             # Rule nos matching the prefix
        self.children = {}                                                                          # Binary Trie, so 2 children
        self.end_node = True
        self.next_level = None

    def __repr__(self) -> str:
        return f"Rules: {self.rules}, NL: {self.next_level}"

class Trie:
    def __init__(self, pfx=None):
        self.root = TrieNode()          
        if pfx:
            self.add(pfx, rule_num=-1)
    
    def __repr__(self) -> str:
        return repr(self.root)

    def add(self, pfx, rule_num):
        current = self.root
        for bit in pfx:
            if bit not in current.children.keys():
                current.children[bit] = TrieNode()
                current.end_node = False                                                            # Added a child, so this is not end node
            current = current.children[bit]
        current.rules.append(rule_num)

        return current

    def get_prefixes(self, prefix):
        prefixes = []
        current = self.root
        
        if current.rules:                                                                           # * match
            prefixes.append(current)

        for bit in prefix:
            if bit in current.children.keys():
                current = current.children[bit]
                if current.rules:
                    prefixes.append(current)
            else:
                current = None
                break
        return prefixes
    
    def visualize(self):
        """Visualize Tries"""
        dot = graphviz.Digraph(comment="Trie Visualization")

        def add_edges(node, prefix=""):
            if node.rules:
                dot.node(prefix, label=f"{prefix}\nRules {node.rules}")
            else:
                dot.node(prefix, label=f"")

            for bit, child in node.children.items():
                child_prefix = f"{prefix}{bit}"
                dot.edge(prefix, child_prefix, label=bit)
                add_edges(child, child_prefix)

            if node.next_level:
                add_edges(node.next_level.root, prefix=f"{prefix}_L2_")
                dot.edge(prefix, f"{prefix}_L2_", label="Next-Level")
                pass

        add_edges(self.root)
        return dot

def ip2binary(ip_addr: str) -> str:
    """
    IP to binary conversion
    """
    b1, b2, b3, b4 = map(int, ip_addr.strip().split("."))
    return f"{(b1):08b}{(b2):08b}{(b3):08b}{(b4):08b}"

class Router:
    def __init__(self, rules_f, ip_f) -> None:
        self.rules_table = []                                                                       # Tuple: (rule_num, addr1, pfx_len1, addr2, pfx_len2)
        self.inputs = []                                                                            # Tuple: (addr1, addr2)
        self.trie_table = Trie()

        with open(rules_f, 'r') as f:
            for i, line in enumerate(f):
                try:
                    entry1, entry2 = map(str, line.strip().split(" "))
                    addr1, pfx_len1 = map(str, entry1.strip().split("/"))
                    addr2, pfx_len2 = map(str, entry2.strip().split("/")) 

                    self.rules_table.append((i, addr1, int(pfx_len1), addr2, int(pfx_len2)))
                except ValueError:
                    print(f"ValueError. Extra \\n encountered at line {i+1}")

        with open(ip_f, 'r') as f:
            for line in f:
                addr1, addr2 = map(str, line.strip().split(" "))
                self.inputs.append((addr1, addr2))
       
        self.__construct_hierarchial_trie()                                                         # Build hierarchial tries

        if len(self.rules_table) <= 10:                                                             # Render L1 trie for smaller inputs
            dot = self.trie_table.visualize()
            dot.render("TG", view=True)

    def __construct_hierarchial_trie(self):        
        for entry in self.rules_table:
            rule_num, addr1, pfx_len1, addr2, pfx_len2 = entry

            addr1 = ip2binary(ip_addr=addr1)
            addr2 = ip2binary(ip_addr=addr2)
            level1_node = self.trie_table.add(addr1[:pfx_len1], rule_num=rule_num)                  # Level 1 trie construction

            if level1_node.next_level == None:                                                      # Level 2 trie construction
                level1_node.next_level = Trie()
                level1_node.next_level.add(addr2[:pfx_len2], rule_num=rule_num)
            else:
                level1_node.next_level.add(addr2[:pfx_len2], rule_num=rule_num)
    
    def __match_fields(self, addr1, addr2):
        A = []                                                                                      # Set of matching prefixes in L1
        R = []                                                                                      # Set of matching prefixes in L2

        A = self.trie_table.get_prefixes(addr1)

        for entry in A:
            l2_node = entry.next_level
            R.extend(l2_node.get_prefixes(addr2))

        rules_matched = []
        if R:
            for node in R:
                rules_matched.extend(node.rules)
        
        return rules_matched

    def run(self, out_f):
        
        with open(out_f, 'w') as f:
            avg_time = 0
            i = 0
            for entry in self.inputs:
                addr1, addr2 = entry
                
                start_time = time.time_ns()
                rules_matched = self.__match_fields(ip2binary(ip_addr=addr1), ip2binary(ip_addr=addr2))
                end_time = time.time_ns()

                time_us = (end_time-start_time)/1000
                avg_time += time_us
                i+=1

                rules_matched = [item+1 for item in rules_matched]                                  # +1 to begin indexing at 1
                # rules_matched = " ".join(str(x) for x in rules_matched)
                f.write(f"{addr1}, {addr2}, {len(rules_matched)}, {rules_matched}, {time_us}\n")
            f.write(f"Average search time is: {(avg_time/i):.3f} microseconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Rules file", type=str, )
    parser.add_argument("-i", help="Input Address file", type=str)
    parser.add_argument("-o", help="Output file", type=str)
    
    args = parser.parse_args()
    
    router = Router(args.p, args.i)
    router.run(args.o)
