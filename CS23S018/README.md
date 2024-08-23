# Virtual Circuit Switching

# List of Files/Directories:
1. main.py: Source file 
2. Makefile: Make build file
3. requirements.txt: Python dependencies 
4. inputs/: Contains topologyfile, connectionsfile
5. outputs/: Contains routingtablefile, forwardingfile, pathsfile
6. helper/: Scripts to generate testcases.
7. log.txt: log file

# How to Run:

## 0. Open Terminal in lab directory

## 1. Setup a virtual environment 
 ```
 $ python3 -m venv venv
 $ source ./venv/bin/activate
 ```
## 2. Install dependencies
 ```
 $ pip install ./requirements.txt
 ```
## 3. There are two ways to run this lab:
### With Make:

* The make file defines command line params with default values:
    | Parameter | Description                   | Default Value     |
    |-----------|-------------------------------|-------------------|
    | TOPO_FILE | Input topology file           | ./inputs/ARPANET-Topo.txt |
    | CONN_FILE | Input connections file.       | ./inputs/ARPANET-300conn.txt |
    | RT_FILE   | Output routing table file.    | ./outputs/rt.txt  |
    | FT_FILE   | Output forwarding table file. |./outputs/ft.txt   |
    | PT_FILE   | Output paths file.            | "./outputs/pt.txt |
    | FLAG      | Metric for path. "hop" or "dist". | hop           |
    | APPROACH  | Flag for Optimistic or Pessimistic approach. "Optimistic": 0, "Pessimistic": 1. | 0 |
        
* Run with default params: ```$ make```

* To run with custom params: ```$ make TOPO_FILE=topo_file_name CONN_FILE=conn_file_name RT_FILE=rt_file_name FT_FILE=ft_file_name PT_FILE=pt_file_name FLAG=hop APPROACH=0```
            
### Without Make/ Directly with python3

* The python file requires command line params:
    | Parameter | Description                   | Required?         |
    |-----------|-------------------------------|-------------------|
    | -top      | Input topology file               | Y             |
    | -conn     | Input connections file.           | Y             |
    | -rt       | Output routing table file.        | Y             |
    | -ft       | Output forwarding table file.     | Y             |
    | -path     | Output paths file.                | Y             |
    | -flag     | Metric for path. "hop" or "dist". | Y             |
    | -p        | Flag for Optimistic or Pessimistic approach. "Optimistic": 0, "Pessimistic": 1. | Y |

* Run:
    1. Get help: ```$ python3 main.py -h```
    2. e.g. ```$ python3 main.py -top filename -conn filename -rt filename -ft filename -path filename -flag hop -p 0```