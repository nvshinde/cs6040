RUN_SCRIPT = ./main.py
OUTPUT_DIR = outputs

# input file
ifndef IN
IN = ./inputs/omega.txt
endif

ifndef SW
SW = Omega
endif

.PHONY: all run

all: run

run: main.py
	python3 $(RUN_SCRIPT) -in $(IN) -sw $(SW)
