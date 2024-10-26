#  WFQ Scheduling

# List of Files/Directories:
1. main.py: Source file 
2. Makefile: Make build file
3. requirements.txt: Python dependencies 
4. inputs/: Contains input files
5. outputs/: Contains system level metrics
6. metrics/: Contains source level and server level metrics, packet generation data (src*-graph.txt) and packet transmission data (graph.txt). These can be plotted with plot-pkt-gen.py and plott.py resp. in helpers/. 

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
## 3. There are two ways to run this lab:
### With Make:

* The make file defines command line params with default values:
    | Parameter | Description                   | Default Value         |
    |-----------|-------------------------------|-----------------------|
    | IN        | Input file                    | ./inputs/input4.txt   |
    | OUT       | Output file                   | ./outputs/output4.txt |
        
* Run with default params: ```$ make```

* To run with custom params: ```$ make IN=input_file_name OUT=output_file_name```
            
### Without Make/ Directly with python3

* The python file requires command line params:
    | Parameter | Description                   | Required?         |
    |-----------|-------------------------------|-------------------|
    | -inp      | Input file                    | Y                 |
    | -out      | Output file                   | Y                 | 

* Run:
    1. Get help: ```$ python3 main.py -h```
    2. e.g. ```$ python3 main.py -inp filename -out filename```