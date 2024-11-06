#!/usr/bin/env python3

class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_node = False

class Trie:
    def __init__(self, data=None):
        self.root = TrieNode()
        if data:
            self.add(data)

    def add(self, data):
        current = self.root
        for char in data:
            if char not in current.children.keys():
                current.children[char] = TrieNode()
            current = current.children[char]
        current.end_node = True

    def contains(self, data):
        current = self.root
        for char in data:
            if char in current.children.keys():
                current = current.children[char]
            else:
                current = None
                break

        return current and current.end_node
    
    def contains_prefix(self, prefix):
        current = self.root

        for char in prefix:
            if char in current.children.keys():
                current = current.children[char]
            else:
                current = None
                break

        if current:
            return self.__contains_prefix(current, prefix)
        else:
            return None

    def __contains_prefix(self, current, prefix):
        result = []
        if current.end_node:
            result.append(prefix)

        for char in current.children.keys():
            result.extend(self.__contains_prefix(current.children[char], prefix+char))

        return result
    
    def delete(self, data):
        current = self.root

        for char in data:
            if char in current.children.keys():
                current = current.children[char]
            else:
                current = None
                break

        if current:
            current.end_node = False

trie = Trie()
trie.add("can")
trie.add("cane")
trie.add("olala")
trie.add("camera")
trie.add("catwalk")

if trie.contains("can"):
    print("True1")

if trie.contains("ohmy"):
    print("True2")
else:
    print("False2")

words = trie.contains_prefix("ca")

for word in words:
    print(word)

trie.delete("olala")
if trie.contains("olala"):
    print("True3")
else:
    print("False")
