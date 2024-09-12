import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import pprint
import logging
import random
import math

OUTFILE = "out.txt"

class Exercise:
    def __init__(self, in_file=None, sw=None) -> None:
        self.in_file = in_file
        self.sw = sw
        self.n = None
        self.a = None
        self.outports = []
        self.network = None
        # parse file
        with open(self.in_file, 'r') as f:
            self.n = int(f.readline())
            self.a = int(f.readline())
            for _ in range(self.a):
                self.outports.append(int(f.readline()))
        

    def run(self) -> None:
        if self.sw == "omega":
            self.omega()
        elif self.sw == "delta":
            self.delta()
        elif self.sw == "benes":
            self.benes()
        else:
            pass
    
    def circular_lshift(self, port, k=1):
        return ((port << k) | (port >> int(math.log2(self.n)) - k)) & (self.n - 1)
    

    def omega(self) -> None:
        bit_len = int(math.log2(self.n))
        num_stages = bit_len
        num_switches = self.n // 2  # switches in a stage

        # Initialize a switch matrix with 'T' mode as default for each switching element
        switch_matrix = [['T' for _ in range(num_stages)] for _ in range(num_switches)]
        
        for i, outport in enumerate(self.outports):
            # Initial perfect shuffle. Before the leftmost stage
            curr_stage_inport = self.circular_lshift(i)

            for stage in range(num_stages):
                # Get the idx of stage
                SE_idx = curr_stage_inport // 2
                
                # Get the ports of the stage element. 1 or 0
                SE_in_port = curr_stage_inport % 2
                SE_out_port = (outport >> (bit_len - stage - 1)) & 1
                
                # Get the outport of the current stage. [0, n)
                curr_stage_outport = SE_idx * 2 + SE_out_port

                # Update mode of switching element
                if SE_in_port == SE_out_port:
                    switch_matrix[SE_idx][stage] = 'T'
                else:
                    switch_matrix[SE_idx][stage] = 'C'

                # Get next stage input port. [0, n).
                curr_stage_inport = self.circular_lshift(int(curr_stage_outport))
        
        with open(OUTFILE, 'w') as f:
            for row in switch_matrix:
                f.write(' '.join(row) + '\n')
            
    def delta(self) -> None:
        """
        Note.
        Delta n/w has internal contention. But as per the constraints given, perfect shuffle before leftmost stage,
        in this assignment, there will be no internal contention.
        """
        bit_len = int(math.log2(self.n))
        num_stages = bit_len
        num_switches = self.n // 2

        # Initialize a switch matrix with 'T' mode as default for each switching element
        switch_matrix = [['T' for _ in range(num_stages)] for _ in range(num_switches)]
        
        for i, outport in enumerate(self.outports):
            # Initial perfect shuffle. Before the leftmost stage
            curr_stage_inport = self.circular_lshift(i)

            for stage in range(num_stages):
                # Get the idx of stage
                SE_idx = curr_stage_inport // 2
                
                # Get the ports of the stage element. 1 or 0
                SE_in_port = curr_stage_inport % 2
                SE_out_port = (outport >> (bit_len - stage - 1)) & 1
                
                # Get the outport of the current stage. [0, n)
                curr_stage_outport = SE_idx * 2 + SE_out_port

                # Update mode of switching element
                if SE_in_port == SE_out_port:
                    switch_matrix[SE_idx][stage] = 'T'
                else:
                    switch_matrix[SE_idx][stage] = 'C'
                
                if SE_out_port == 0:
                    # Upper port of a switch
                    tmp = SE_idx % (2**(num_stages - 1 - stage))
                    if (tmp) < num_switches // (2**(stage+1)):
                        # switch belongs to upper half of the stage
                        curr_stage_inport = curr_stage_outport
                    else:
                        # switch belongs to lower half of the stage 
                        # curr_stage_inport = curr_stage_outport - ((num_switches // 2**stage) // (2**(stage+1))) - 1
                        curr_stage_inport = curr_stage_outport - (num_switches // 2**(2*stage+1)) - 1
                else:
                    # Lower port of a switch
                    tmp = SE_idx % (2**(num_stages - 1 - stage))
                    if (tmp) >= num_switches // (2**(stage+1)):
                        # switch belongs to lower half of the stage
                        curr_stage_inport = curr_stage_outport
                    else:
                        # swtich belongs to upper half of the stage
                        # curr_stage_inport = curr_stage_outport + ((num_switches // 2**stage) // (2**(stage+1))) + 1
                        curr_stage_inport = curr_stage_outport + (num_switches // 2**(2*stage+1)) + 1


        with open(OUTFILE, 'w') as f:
            for row in switch_matrix:
                f.write(' '.join(row) + '\n')
    

    def circular_rshift(self, num, stage=0, k=1):
        """Specifically for Benes, no. of bits is varied according to stage"""
        return ((num >> k) |  (num << int(math.log2(self.n/(2**stage))) - k)) & (int(self.n/(2**stage)) - 1)
    
    def print_matrix(self, matrix):
        for row in matrix:
            for item in row:
                print(item['mode'], end=' ')
            print()

    def benes(self) -> None:
                
        num_stages = int(math.log2(self.n)) * 2 - 1
        num_switches = int(self.n/2)
        # switch_matrix = [[{'mode': 'z', 'op0': '', 'op1': '', 'ip0': '', 'ip1': '', 'set' : 0} for _ in range(num_stages)] for _ in range(num_switches)]
        switch_matrix = [[{'mode': '-', 'set' : 0} for _ in range(num_stages)] for _ in range(num_switches)]
        # switch_matrix[0][1]['mode'] = 'T'
        # pprint.pprint(switch_matrix)

        for i, outport in enumerate(self.outports):
            lcurr_stage_global_inport = i
            rcurr_stage_global_inport = outport
            
            for stage in range(num_stages//2): 
                """Go till middle - 1 stage only"""
                lstage = stage
                lcurr_stage_global_inport = lcurr_stage_global_inport
                lcurr_stage_sub_inport = lcurr_stage_global_inport % int((self.n / (2**stage)))

                # matrix params
                l_mat_col = stage
                l_mat_row = lcurr_stage_global_inport // 2
                r_mat_col = num_stages - stage - 1
                r_mat_row = rcurr_stage_global_inport // 2

                rstage = stage # num_stages - stage - 1
                rcurr_stage_global_inport = rcurr_stage_global_inport
                rcurr_stage_sub_inport = rcurr_stage_global_inport % (self.n / (2**stage))

                # rSE_inport = rcurr_stage_global_inport % 2
                print(f"Stage: {stage}, lcsgi: {lcurr_stage_global_inport}, lcssi: {lcurr_stage_sub_inport}, rcsgi: {rcurr_stage_global_inport}, rcssi: {rcurr_stage_global_inport}, l_MATRIX: [{l_mat_row}, {l_mat_col}], r_MATRIX: [{r_mat_row}, {r_mat_col}]")
                if switch_matrix[l_mat_row][l_mat_col]['set'] == 0 and switch_matrix[r_mat_row][r_mat_col]['set'] == 0:
                    """No switch is set"""
                    """Thus we can set left switch to default 'T' and set right accordingly"""
                    switch_matrix[l_mat_row][l_mat_col]['set'] = 1
                    switch_matrix[l_mat_row][l_mat_col]['mode'] = 'T'


                    lSE_inport = lcurr_stage_sub_inport % 2
                    lSE_outport = None
                    if (lSE_inport == 0):
                        lSE_outport = 0
                    else:
                        lSE_outport = 1

                    if lSE_outport == 0:
                        """Upper part of the subnetwork"""
                        """Accordingly set the right side switch"""
                        switch_matrix[r_mat_row][r_mat_col]['set'] = 1
                        rSE_inport = rcurr_stage_sub_inport % 2
                        if rSE_inport == 0:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'T'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport, stage=stage)
                        else:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'C'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport - 1, stage=stage)
                    else:
                        """Lower part of the subnetwork"""
                        """Accordingly set the right side switch"""
                        switch_matrix[r_mat_row][r_mat_col]['set'] = 1
                        rSE_inport = rcurr_stage_sub_inport % 2
                        if rSE_inport == 0:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'C'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport + 1, stage=stage)
                        else:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'T'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport, stage=stage)

                    """Compute the global input for the next stage"""
                    # TODO: BUG?
                    lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport, stage=stage)


                elif switch_matrix[l_mat_row][l_mat_col]['set'] == 0 and switch_matrix[r_mat_row][r_mat_col]['set'] == 1:
                    """Right switch is set"""
                    """Set the left switch accordingly"""
                    mode = switch_matrix[r_mat_row][r_mat_col]['mode']
                    rSE_inport = rcurr_stage_sub_inport % 2
                    rSE_outport = None
                    if (mode == 'T'):
                        rSE_outport = rSE_inport
                    else:
                        rSE_outport =  1 - rSE_inport

                    if rSE_outport == 0:
                        """Upper part of the network"""
                        switch_matrix[l_mat_row][l_mat_col]['set'] = 1
                        lSE_inport = lcurr_stage_sub_inport % 2
                        if lSE_inport == 0:
                            switch_matrix[l_mat_row][l_mat_col]['mode'] = 'T'
                            lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport, stage=stage)
                        else:
                            switch_matrix[l_mat_row][l_mat_col]['mode'] = 'C'
                            lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport - 1, stage=stage)
                    else:
                        """Lower part of the network"""
                        switch_matrix[l_mat_row][l_mat_col]['set'] = 1
                        lSE_inport = lcurr_stage_sub_inport % 2
                        if lSE_inport == 0:
                            switch_matrix[l_mat_row][l_mat_col]['mode'] = 'C'
                            lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport + 1, stage=stage)
                        else:
                            switch_matrix[l_mat_row][l_mat_col]['mode'] = 'T'
                            lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport, stage=stage)

                elif switch_matrix[l_mat_row][l_mat_col]['set'] == 1 and switch_matrix[r_mat_row][r_mat_col]['set'] == 0:
                    """Left swtich is set"""
                    """Set the right switch accordingly"""
                    mode = switch_matrix[l_mat_row][l_mat_col]['mode'] 
                    lSE_inport = lcurr_stage_sub_inport % 2
                    lSE_outport = None
                    if (mode == 'T'):
                        lSE_outport = lSE_inport
                    else:
                        lSE_outport = 1 - lSE_inport
                    
                    if lSE_outport == 0:
                        """Upper part of the subnetwork"""
                        switch_matrix[r_mat_row][r_mat_col]['set'] = 1
                        rSE_inport = rcurr_stage_sub_inport % 2
                        if rSE_inport == 0:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'T'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport, stage=stage)

                        else:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'C'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport - 1, stage=stage)

                    else:
                        """Lower part of the subnetwork"""
                        switch_matrix[r_mat_row][r_mat_col]['set'] = 1
                        rSE_inport = rcurr_stage_sub_inport % 2
                        if rSE_inport == 0:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'C'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport + 1, stage=stage)
                        else:
                            switch_matrix[r_mat_row][r_mat_col]['mode'] = 'T'
                            rcurr_stage_global_inport = self.circular_rshift(rcurr_stage_global_inport, stage=stage)

                    lcurr_stage_global_inport = self.circular_rshift(lcurr_stage_global_inport, stage=stage)

                    
                elif switch_matrix[l_mat_row][l_mat_col]['set'] == 1 and switch_matrix[r_mat_row][r_mat_col]['set'] == 1:
                    """Both switches are set"""
                    
                    """Check left switch config and set next stage input accordingly"""
                    lmode = switch_matrix[l_mat_row][l_mat_col]['mode']
                    

                    rmode = switch_matrix[r_mat_row][r_mat_col]['mode']

                print(f"Input: {i}, Connection: {outport}, Stage: {stage}.")
                self.print_matrix(switch_matrix)
            # Middle stage connect

    def benes_back_tracking(self):
        num_stages = int(math.log2(self.n)) * 2 - 1
        num_switches = int(self.n/2)
        switch_matrix = [[{'mode': 'z', 'op0': '', 'op1': '', 'ip0': '', 'ip1': ''} for _ in range(num_stages)] for _ in range(num_switches)]

        for i, outport in enumerate(self.outports):
            # Initially
            curr_stage_inport = i
            curr_SE_inport = i % 2
            curr_SE_idx = curr_stage_inport // 2
            for stage in range(num_stages):
                if stage < num_stages // 2:
                    """Left part of the network"""
                    col = stage
                    row = curr_stage_inport // 2

                    if switch_matrix[row][col]['mode'] == 'z':
                        switch_matrix[row][col]['mode'] = 'T'
                        curr_stage_inport = self.circular_rshift(curr_stage_inport, stage=stage)
                        pass
                    elif switch_matrix[row][col]['mode'] == 'T':
                        pass
                    elif switch_matrix[row][col]['mode'] == 'C':
                        pass
                    else:
                        pass
                    pass
                else:
                    """Right part of the network"""
                    col = stage
                    # row = 
                    pass
                pass
            pass


if __name__ == "__main__":
    random.seed(0)

    logging.basicConfig(level=logging.DEBUG, filename="log.txt", filemode='w', format="[%(asctime)s] [%(levelname)s]:\n\t %(message)s")

    parser = argparse.ArgumentParser(prog="MIN Switching Configuration",
                                     description="")
    parser.add_argument('-inf', help="'in' arg doesnt work. Use 'inf'. Input File", action="store", required=True, type=str)
    parser.add_argument('-sw', help="Network type. 'omega', 'benes', 'delta'", action="store", required=True, type=str)

    args = parser.parse_args()
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'outputs')
    log_dir = os.path.join(cwd, 'logs')

    # exercise = Exercise(in_file=args.in, network=args.sw)
    exercise = Exercise(in_file=args.inf, sw=args.sw)
    exercise.run()