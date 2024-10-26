RUN_SCRIPT = ./main.py

# input file
ifndef IN
IN = ./inputs/input4.txt
endif

ifndef OUT
OUT = ./outputs/output4.txt
endif

.PHONY: all run

all: run

run: main.py
	python3 $(RUN_SCRIPT) -inp $(IN) -out $(OUT)