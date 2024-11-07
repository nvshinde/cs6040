#! /usr/bin/env python3
import sys

if sys.argv[2] == 'r':
    with open(sys.argv[1], 'r') as f:
        for i, line in enumerate(f):
            entry1, entry2 = map(str, line.strip().split(" "))
            addr1, pfx_len1 = map(str, entry1.strip().split("/"))
            addr2, pfx_len2 = map(str, entry2.strip().split("/")) 

            b1, b2, b3, b4 = map(int, addr1.strip().split("."))
            if b1 > 255 or b2 > 255 or b3 > 255 or b4 > 255:
                print(f"Problem @ line {i+1} field 1") 
            
            b1, b2, b3, b4 = map(int, addr2.strip().split("."))
            if b1 > 255 or b2 > 255 or b3 > 255 or b4 > 255:
                print(f"Problem @ line {i+1} field 2")

if sys.argv[2] == 'a':
    with open(sys.argv[1], 'r') as f:
        for i, line in enumerate(f):
            entry1, entry2 = map(str, line.strip().split(" "))

            b1, b2, b3, b4 = map(int, entry1.strip().split("."))
            if b1 > 255 or b2 > 255 or b3 > 255 or b4 > 255:
                print(f"Problem @ line {i+1} field 1") 
            
            b1, b2, b3, b4 = map(int, entry2.strip().split("."))
            if b1 > 255 or b2 > 255 or b3 > 255 or b4 > 255:
                print(f"Problem @ line {i+1} field 2")
