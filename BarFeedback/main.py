#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from runNbackTask import runNbackTask
from runStroopTask import runStroopTask
from expyriment import control, stimuli, design, misc, io
import datetime

screen_height = 600
screen_width = 800
use_develop_mode = False

def ask_for_task():
    develop_mode = use_develop_mode
    design.defaults.experiment_background_colour = misc.constants.C_GREY
    design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
    control.set_develop_mode(develop_mode)
    exp = control.initialize()
    control.start(exp, skip_ready_screen=True)
    canvas = stimuli.BlankScreen()
    N_back = stimuli.Rectangle(size=(100, 80), position=(200, 0))
    text_N_back = stimuli.TextLine(text="N back", position=N_back.position,
                                     text_colour=misc.constants.C_WHITE)
    Stroop = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
    text_Stroop = stimuli.TextLine(text="Stroop", position=Stroop.position,
                                  text_colour=misc.constants.C_WHITE)

    N_back.plot(canvas)
    text_N_back.plot(canvas)

    Stroop.plot(canvas)
    text_Stroop.plot(canvas)

    exp.mouse.show_cursor()
    canvas.present()

    while True:
        id, pos, _rt = exp.mouse.wait_press()

        if N_back.overlapping_with_position(pos):
            exp.mouse.hide_cursor()
            return 'n_back', exp
        elif Stroop.overlapping_with_position(pos):
            exp.mouse.hide_cursor()
            return 'stroop', exp

task, exp = ask_for_task();
if task == "n_back":
    runNbackTask(screen_height, screen_width, exp, use_develop_mode)
else:
    runStroopTask(screen_height, screen_width, exp, use_develop_mode)


