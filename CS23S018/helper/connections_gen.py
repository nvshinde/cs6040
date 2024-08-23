#!/usr/bin/python3

import random
import argparse

def generate_requests(n, r, bmin, bmax, conn_f):

    with open(conn_f, 'w') as f:
        f.write(f"{r}\n")
        for _ in range(r):
            src = random.randint(0, n-1)
            dst = random.randint(0, n-1)
            while dst == src:
                dst = random.randint(0, n-1)

            bi_min = random.randint(0, bmax)
            bi_max = random.randint(bi_min, bmax)
            bi_ave = random.randint(bi_min, bi_max)

            f.write(f"{src} {dst} {bi_min} {bi_ave} {bi_max}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Connections generator")
    parser.add_argument('-n', help="No. of node", action="store", type=int, required=True)
    parser.add_argument('-r', help="No. of requests", action="store", type=int, required=True)
    parser.add_argument('-bmin', help="Min bandwidth for any connection", action="store", type=int, required=True)
    parser.add_argument('-bmax', help="Max bandwidth for any connection", action="store", type=int, required=True)
    parser.add_argument('-c', help="O/p Connections file", action="store", type=str, default="conn.txt")
    args = parser.parse_args()

    generate_requests(n=args.n, r=args.r, bmin=args.bmin, bmax=args.bmax, conn_f=args.c)