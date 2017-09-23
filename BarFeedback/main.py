#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division

from expyriment import control, stimuli, io, design, misc
import sched, time

control.set_develop_mode(True)
# settings
design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
red_part_length = 200
yellow_part_length = 300
green_part_length = 200
lineY_position = 250
line_start_position = 0 - (red_part_length + yellow_part_length + green_part_length)/2

def getLineMiddlePosition(lineStart, lineLength):
    return lineStart + lineLength/2

def paintLine(line_length, positionX, color, canvas):
   line = stimuli.Rectangle(size=(line_length, 10), position=[positionX, lineY_position],
                                colour=color)
   line.plot(canvas)

def line_bisection_task(position):
    mark_position = 10

    while True:
        canvas = stimuli.BlankScreen()
        mark_position -= 10
        paintLine(red_part_length, line_start_position + red_part_length / 2, misc.constants.C_RED, canvas)
        paintLine(yellow_part_length, line_start_position + red_part_length + yellow_part_length / 2 \
                  , misc.constants.C_YELLOW, canvas)
        paintLine(green_part_length, line_start_position + red_part_length + yellow_part_length \
                  + green_part_length / 2
                  , misc.constants.C_GREEN, canvas)

        # plot button and mark line on canvas

        markline = stimuli.Rectangle(size=(4, 25),
                                     position=(mark_position, lineY_position),
                                     colour=misc.constants.C_BLACK)
        markline.plot(canvas)
        # present stimulus
        canvas.present()
        time.sleep(2)

### init ###
exp = control.initialize()

### start ###
control.start(exp)
exp.mouse.show_cursor()

# trial loop
while True:
    # find random position
    rx, ry = (0, lineY_position)
    pos = [rx, ry]
    # present task
    judgment = line_bisection_task(position=pos)
    # save data
    exp.data.add(pos +[judgment])
    # ask for new trail


## end##
control.end()
