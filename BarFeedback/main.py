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
import pylsl
from pylsl import StreamInfo, StreamOutlet

screen_height = 600
screen_width = 800
use_develop_mode = True


def ask_for_task():

    canvas = stimuli.BlankScreen()
    develop_mode = use_develop_mode
    design.defaults.experiment_background_colour = misc.constants.C_GREY
    design.defaults.experiment_foreground_colour = misc.constants.C_BLACK


    N_back = stimuli.Rectangle(size=(100, 80), position=(200, 0))
    text_N_back = stimuli.TextLine(text="N back", position=N_back.position,
                                     text_colour=misc.constants.C_WHITE)
    Stroop = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
    text_Stroop = stimuli.TextLine(text="Stroop", position=Stroop.position,
                                  text_colour=misc.constants.C_WHITE)


    exit = stimuli.Rectangle(size=(100, 80), position=(0, -200))
    text_exit = stimuli.TextLine(text="Exit", position=exit.position,
                                  text_colour=misc.constants.C_WHITE)
    N_back.plot(canvas)
    text_N_back.plot(canvas)

    Stroop.plot(canvas)
    text_Stroop.plot(canvas)

    exit.plot(canvas)
    text_exit.plot(canvas)

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
        elif exit.overlapping_with_position(pos):
            exp.mouse.hide_cursor()
            return 'exit', exp

info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)
control.set_develop_mode(use_develop_mode)
exp = control.initialize()
control.start(exp, skip_ready_screen=True)

start_new_exp = False
while True:
    if start_new_exp == True:
        exp = control.initialize()
        control.start(exp, skip_ready_screen=True)

    task, exp = ask_for_task()
    if task == "n_back":
        nBack = runNbackTask(exp.screen.window_size[1], exp.screen.window_size[0], exp, use_develop_mode,\
                     str(exp.data._subject), outlet)
        start_new_exp = nBack.start_run();

    elif task == "stroop":
         stroop = runStroopTask(exp.screen.window_size[1], exp.screen.window_size[0], exp, use_develop_mode,\
                      str(exp.data._subject), outlet)
         start_new_exp = stroop.start_run()
    else:
        break



