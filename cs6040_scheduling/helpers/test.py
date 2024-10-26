import multiprocessing as mp
import time

prx, ptx = mp.Pipe()

def proc_fn(prx):
    ptx.close()
    while True:
        try:
            if prx.poll():
                data = prx.recv()
                print("data available:", data)
                print("doing something")
            else:
                # If no data is available, you could add a small sleep to avoid busy waiting
                time.sleep(0.1)
        except EOFError:
            print("EOFError: Pipe closed")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

proc = mp.Process(target=proc_fn, args=(prx,))
proc.start()

for i in range(8):
    ptx.send(f"{i}")
    time.sleep(1)
    if i > 3:
        ptx.close()
        break

ptx.close()
prx.close()
print("connection close")

proc.join()