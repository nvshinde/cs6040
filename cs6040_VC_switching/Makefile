RUN_SCRIPT = ./main.py
LOG_DIR = logs
OUTPUT_DIR = outputs

# topology file
ifndef TOPO_FILE
TOPO_FILE = ./inputs/topo.txt
endif

# connections file
ifndef CONN_FILE
CONN_FILE = ./inputs/conn.txt
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
FLAG = hop

# APPROACH: pessimistic or optimistic
APPROACH = 0

.PHONY: all run dirs

all: run

run: dirs main.py $(LOG_DIR) $(OUTPUT_DIR)
	python3 $(RUN_SCRIPT) -top $(TOPO_FILE) -conn $(CONN_FILE) -rt $(RT_FILE) -ft $(FT_FILE) -path $(PT_FILE) -flag $(FLAG) -p $(APPROACH)

dirs: 
	rm -rf $(LOG_DIR) $(OUTPUT_DIR)
	mkdir $(LOG_DIR) $(OUTPUT_DIR)