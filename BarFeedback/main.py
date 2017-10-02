#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from nback import Nback
from restBlock import RestBlock
from stressEvaluation import StressEvaluation
from writeToExcel import WriteToExcel


blocks = [(1,'a'), (3,'a'), (2, 'a'), (3, 'b'), (1, 'b'), (2, 'b')]
experiment = Nback(True)
stress_evaluation_log = WriteToExcel("stress_evaluation", ["block_type", "stressful", "painful", "unpleasant"])
screen_height = 600
screen_width = 800

index = 0
for block in blocks:
    if index > 2:
        break
    rest = RestBlock(str(block[0]), experiment.exp)
    n_back = experiment.run(block[0], block[1])
    stress_evaluation = StressEvaluation(experiment.exp,\
                                         ["how stressful", "how painful", "how unpleasant"],\
                                         screen_height, screen_width)
    row_to_insert = stress_evaluation.get_positions_array_in_precentage()
    row_to_insert.insert(0, str(block[0]) + block[1])
    stress_evaluation_log.add_row(row_to_insert)
    index += 1

stress_evaluation_log.close_file()




from expyriment import control, stimuli, io, design, misc
import sched, time

