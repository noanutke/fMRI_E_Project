#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import pygame
from expyriment import control, stimuli, io, design, misc
import sched, time


class FeedbackBar:
    red_part_length = 200
    yellow_part_length = 300
    green_part_length = 200
    lineY_position = 250
    whole_length = red_part_length + yellow_part_length + green_part_length
    line_start_position = 0 - whole_length / 2
    default_position_update = 50
    trial_number = 0
    mark_updates = []
    trials_in_danger = 0


    def __init__(self, initial_mark_position,  rt_average, show_alarms = False):
        self.mark_position = initial_mark_position
        self.rt_average = rt_average
        self.show_alarms = show_alarms
        self.alarm_on = False

    def get_line_middle_position(lineStart, lineLength):
        return lineStart + lineLength / 2

    def paint_line_part(self, line_length, position_x, color, canvas):
        line = stimuli.Rectangle(size=(line_length, 10), position=[position_x, self.lineY_position],
                                 colour=color)
        line.plot(canvas)

    def write_sucess(self, position, canvas):
        text = stimuli.TextLine("success", position)
        text.plot(canvas)

    def write_failure(self, position, canvas):
        text = stimuli.TextLine("failure", position)
        text.plot(canvas)

    def paint_whole_line(self, canvas, is_error, rt = None, updatePosition = False):
        cross = stimuli.FixCross((50,50), (0,0), 5)
        cross.plot(canvas)
        if self.show_alarms == False:
            return

        if updatePosition == True:
            self.update_mark_position(is_error, rt)

        self.paint_line_part(self.red_part_length, self.line_start_position + self.red_part_length / 2, misc.constants.C_RED, canvas)
        self.paint_line_part(self.yellow_part_length, self.line_start_position + self.red_part_length + self.yellow_part_length / 2 \
                  , misc.constants.C_YELLOW, canvas)
        self.paint_line_part(self.green_part_length, self.line_start_position + self.red_part_length + self.yellow_part_length \
                  + self.green_part_length / 2
                  , misc.constants.C_GREEN, canvas)

        self.write_sucess((self.line_start_position + self.whole_length - 10, self.lineY_position+20), canvas)
        self.write_failure((self.line_start_position, self.lineY_position+20), canvas)

        # plot button and mark line on canvas

        markline = stimuli.Rectangle(size=(4, 25),
                                     position=(self.mark_position, self.lineY_position),
                                     colour=misc.constants.C_BLACK)

        markline.plot(canvas)

    def set_mark_position(self, new_position):
        self.mark_position = new_position



    def update_mark_position(self, is_error, rt = None):
        direction = 0
        if is_error == True:
            self.alarm_on = True
            direction = -1
        elif rt != None and rt > self.rt_average:
            self.alarm_on = True
            direction = -1
        elif rt != None and rt <= self.rt_average:
            self.alarm_on = False
            direction = 1
        else:
            self.alarm_on = False
            direction = 0

        if self.mark_position + self.default_position_update * direction >= self.line_start_position and \
                self.mark_position + self.default_position_update * direction <= self.line_start_position + self.whole_length:

            self.mark_position += self.default_position_update * direction

    def default_update_mark_position(self):
        if len(self.mark_updates) == 0:
            return
        self.mark_position = self.mark_updates[self.trial_number]
        self.trial_number += 1

    def is_in_red(self):
        if self.mark_position < self.line_start_position + self.red_part_length:
            return True
        else:
            return False

    def is_in_danger(self):
        if self.mark_position < self.line_start_position + self.red_part_length - 50:
            return True
        else:
            return False

    def is_aversive_stimuli_fade_in(self):
        if self.trials_in_danger == 1:
            return True
        else:
            return False

    def is_aversive_stimuli_fade_out(self):
        if self.trials_in_danger == 5:
            return True
        else:
            return False

    def is_aversive_stimuli_full(self):
        if self.trials_in_danger > 1 and self.trials_in_danger < 5:
            return True
        else:
            return False

    def update_trials_in_danger(self):
        if len(self.mark_updates) == 0:
            return
        if self.is_in_red():
            self.trials_in_danger += 1
        else:
            self.trials_in_danger = 0

    def is_feedback_bar_on(self):
        if len(self.mark_updates) == 0:
            return False
        return True


    def is_alarm_on(self):
        return self.alarm_on