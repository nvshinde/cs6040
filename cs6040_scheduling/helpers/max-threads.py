import threading
import time

def athread():
    time.sleep(1000)

def main():
    threads = 0
    while True:
        try:
            x = threading.Thread(target=athread, daemon=True)
            threads += 1
            x.start()
        except RuntimeError:
            break
    print(f"Max Threads: {threads}")

main()