from multiprocessing import Process
import os

processes = []
num_processes = os.cpu_count()
print(num_processes)

def sqr(i):
    print(i)

for i in range(16):
    p = Process(target=sqr, args=(i, ))
    processes.append(p)

for p in processes:
    p.start()

for p in processes:
    p.join()

print("end main")