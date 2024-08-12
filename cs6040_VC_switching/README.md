# Lab 1: Virtual Circuit Switching

# List of Files/Directories:
1. main.py: Source file 
2. Makefile: Make build file
3. requirements.txt: Python dependencies 
4. inputs: Directory for inputs. Contains topologyfile, connectionsfile
5. outputs: Directory for outputs. Contains routingtablefile, forwardingfile, pathsfile
6. logs: Logging directory

# How to Run:

There are two ways to run this lab:

1. With Make

2. Without Make
 * Setup a virtual environment 
 ```
 python3 -m venv venv
 . ./venv/bin/activate
 ```
 * Install dependencies
 ```
 pip install ./requirements.txt
 ```