import subprocess
import time
import sys

def run():
    print("--- FIRST RUN (Crashing after 5 seconds) ---")
    p = subprocess.Popen(["python", "demo_phase23_2.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    start_time = time.time()
    crashed = False
    
    while True:
        line = p.stdout.readline()
        if not line and p.poll() is not None:
            break
        if line:
            sys.stdout.write(line)
            sys.stdout.flush()
            
        if not crashed and time.time() - start_time > 5:
            p.stdin.write("\n")
            p.stdin.flush()
            crashed = True

    print("--- SECOND RUN (Resuming) ---")
    p2 = subprocess.Popen(["python", "demo_phase23_2.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while True:
        line = p2.stdout.readline()
        if not line and p2.poll() is not None:
            break
        if line:
            sys.stdout.write(line)
            sys.stdout.flush()

if __name__ == "__main__":
    run()
