RUN_SCRIPT = ./main.py
OUTPUT_DIR = outputs

# topology file
ifndef TOPO_FILE
TOPO_FILE = ./inputs/ARPANET-Topo.txt
endif

# connections file
ifndef CONN_FILE
CONN_FILE = ./inputs/ARPANET-100conn.txt
endif

# routing table file
ifndef RT_FILE
RT_FILE = ./outputs/rt.txt
endif

# forwarding file
ifndef FT_FILE
FT_FILE = ./outputs/ft.txt
endif

# pathsfile
ifndef PT_FILE
PT_FILE = ./outputs/pt.txt
endif

# flag
ifndef FLAG
	FLAG = dist
endif

# APPROACH: pessimistic or optimistic
ifndef APPROACH
	APPROACH = 0
endif

.PHONY: all run

all: run

run: main.py
	python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag $(FLAG) -p $(APPROACH)

# run: main.py
# python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag hop -p 0
# python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag hop -p 1
# python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag dist -p 0
# python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag dist -p 1
