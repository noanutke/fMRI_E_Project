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
import datetime


def evaluate_stress(block_title_suffix = ""):
    stress_evaluation = SelfReport(experiment.exp, \
                                   [["not at all", "extremely"], \
                                    ["not at all", "extremely"], ["not at all", "extremely"]], \
                                   ["how stressful do you feel",\
                                    "how in pain do you feel", "how unpleasant do you feel"], \
                                   screen_height, screen_width)
    row_to_insert = stress_evaluation.get_positions_array_in_precentage()
    row_to_insert.insert(0, str(block[0]) + block[1] + block_title_suffix)
    stress_evaluation_log.add_row(row_to_insert)


def evaluate_load(block_title_suffix = ""):
    cognitive_evaluation = SelfReport(experiment.exp, \
                                      [["Low", "High"], ["Low", "High"], ["Low", "High"], \
                                       ["Good", "Poor"], ["Low", "High"], ["Low", "High"]], \
                                      ["Mental Demand", "Physical Demand", \
                                       "Temporal Demand", "Performance", \
                                       "Effort", "Frustration"], \
                                      screen_height, screen_width)
    row_to_insert = cognitive_evaluation.get_positions_array_in_precentage()
    row_to_insert.insert(0, str(block[0]) + block[1] + block_title_suffix)
    cognitive_load_log.add_row(row_to_insert)

#blocks = [(1,'p', 'v'), (1,'c')]
blocks_practice = [(1,'p', 'v'), (1,'p', 'a'), (1,'p')]
blocks_no_stress = [(1,'c'), (2,'c'), (3, 'c')]
blocks_sound = [(1,'a'), (2,'a'), (3, 'a')]
blocks_pain = [(1, 'b'), (2, 'b'), (3, 'b')]

tests = blocks_practice + blocks_no_stress

all_blocks_pain_first = blocks_practice + blocks_no_stress + blocks_pain + blocks_sound

all_blocks_sound_first = blocks_practice + blocks_no_stress + blocks_sound + blocks_pain

instructions_folder = "instructions_pilot_mode"
use_pilot_mode = True
use_develop_mode = True

start_time = datetime.datetime.now()
experiment = Nback(use_develop_mode, start_time) #use develop mode, use aversive sound
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
block_type = None
for block in tests:
    #if index > 2:
        #break
    stay_on_block = True
    stimuli_type = "both" if len(block) == 2 else block[2]
    if block_type != block[1] and use_pilot_mode == True:
        text_title = stimuli.TextLine("Press space to start new condition", (0, 0), text_size=(50))
        canvas = stimuli.BlankScreen()
        text_title.plot(canvas)
        canvas.present()
        key, rt = experiment.exp.keyboard.wait([continue_key])

    block_type = block[1]
    while stay_on_block:

        if(index == 3): # no stress
            evaluate_stress("_before")

        rest = RestBlock(str(block[0]), block_type, stimuli_type, experiment.exp, use_pilot_mode,\
                         instructions_folder)

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

