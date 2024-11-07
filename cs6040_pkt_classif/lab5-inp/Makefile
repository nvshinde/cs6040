all: rules inputs rules16 inputs16

rules: pktclf.c
	gcc -o $@ $< -lm

rules16: pktclf-16W.c
	gcc -o $@ $< -lm

inputs: pktinfgen.c
	gcc -o $@ $< -lm

inputs16: pktinfgen.c
	gcc -o $@ $< -lm
