#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from nback import Nback
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io


def evaluate_stress():
    stress_evaluation = SelfReport(experiment.exp, \
                                   [["not at all", "extremely"], \
                                    ["not at all", "extremely"], ["not at all", "extremely"]], \
                                   ["how stressful do you feel",\
                                    "how in pain do you feel", "how unpleasant do you feel"], \
                                   screen_height, screen_width)
    row_to_insert = stress_evaluation.get_positions_array_in_precentage()
    row_to_insert.insert(0, str(block[0]) + block[1])
    stress_evaluation_log.add_row(row_to_insert)


def evaluate_load():
    cognitive_evaluation = SelfReport(experiment.exp, \
                                      [["Low", "High"], ["Low", "High"], ["Low", "High"], \
                                       ["Good", "Poor"], ["Low", "High"], ["Low", "High"]], \
                                      ["Mental Demand", "Physical Demand", \
                                       "Temporal Demand", "Performance", \
                                       "Effort", "Frustration"], \
                                      screen_height, screen_width)
    row_to_insert = cognitive_evaluation.get_positions_array_in_precentage()
    row_to_insert.insert(0, str(block[0]) + block[1])
    cognitive_load_log.add_row(row_to_insert)

#blocks = [(1,'p', 'v'), (1,'c')]
blocks_practice = [(1,'p', 'v'), (1,'p', 'a'), (1,'p')]
blocks_no_stress = [(1,'c'), (2,'c'), (3, 'c')]
blocks_sound = [(1,'a'), (2,'a'), (3, 'a')]
blocks_pain = [(1, 'b'), (2, 'b'), (3, 'b')]


#blocks = [(1,'a'), (3,'a'), (2, 'a'), (3, 'b'), (1, 'b'), (2, 'b')]
use_develop_mode = False
wait_for_key = True
experiment = Nback(use_develop_mode, False) #use develop mode, use aversive sound
stress_evaluation_log = WriteToExcel("stress_evaluation", ["block_type", "Stressful", "Painful", "Unpleasant"])
cognitive_load_log = WriteToExcel("cognitive_load_evaluation", ["block_type",\
                                                                "Mental Demand", "Physical Demand",\
                                                                "Temporal Demand", "Performance",
                                                                "Effort", "Frustration"])
screen_height = 600
screen_width = 800

continue_key = misc.constants.K_SPACE
repeat_block_key = misc.constants.K_0
index = 0
for block in blocks_pain:
    #if index > 2:
        #break
    stay_on_block = True
    while stay_on_block:
        stimuli_type = "both" if len(block) == 2 else block[2]
        block_type = block[1]
        if(index == 0 and block_type == 'c'): # not in practice
            evaluate_stress()

        rest = RestBlock(str(block[0]), block_type, stimuli_type, experiment.exp)

        if wait_for_key == True:
            key, rt = experiment.exp.keyboard.wait([continue_key])

        n_back = experiment.run(block[0], block_type, stimuli_type)

        if block_type == 'p':
            key, rt = experiment.exp.keyboard.wait([continue_key, repeat_block_key])
            if key is continue_key:
                stay_on_block = True
            else:
                stay_on_block = False
        else:
            stay_on_block = False
            evaluate_stress()
            evaluate_load()

    index += 1

stress_evaluation_log.close_file()



from expyriment import control, stimuli, io, design, misc
import sched, time

