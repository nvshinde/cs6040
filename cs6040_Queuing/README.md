# Queuing in a Packet Switch

# List of Files/Directories:
1. main.py: Source file 
2. requirements.txt: Python dependencies 
4. outputs/: Contains outputs for each of the queuing disciplines

# How to Run:

## 0. Open Terminal in lab directory

## 1. Setup a virtual environment 
 ```
 $ python3 -m venv venv
 $ source ./venv/bin/activate
 ```
## 2. Install dependencies
 ```
 $ pip install -r ./requirements.txt
 ```
## 3. Running this lab:

* The python file requires command line params:
    | Parameter | Description                                           | Default Values |
    |-----------|-------------------------------------------------------|----------------|
    | -N        | No. of ports in a switch                              | 8              |
    | -B        | Buffer Size                                           | 10             |
    | -p        | Probability of packet generation at a switch          | 0.5            |
    | -q        | Queue type: NOQ, INQ, CIOQ                            | INQ            |
    | -K        | Switch Backplane speedup for CIOQ                     | 0.4*N          |
    | -L        | Num buffered pkts at each i/p Q in CIOQ               | 0.4*N          | 
    | -o        | Output file                                           | out.txt        |
    | -T        | Maxslots. This specifies the simulation time in slots | 10000          |
    | -g        | Generate graphs? Y/N. (Only for graphs data)          | N              |
    | -gf       | Graph data output file (Only for graph data)          | graph.txt      |

* Run:
    1. Get help: ```$ python3 main.py -h```
    2. e.g. ```$ python3 main.py -N 32 -p 0.75 -q CIOQ -L 13 -K 3 -T 100000```

# Bugs:
1. The code crashes in case of CIOQ, if correct values of L and K are not given with respect to N. e.g. If N=2, then L/K = int(0.4*N) = int (0.8) = 0.