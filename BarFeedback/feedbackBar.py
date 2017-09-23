#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

from expyriment import control, stimuli, io, design, misc
import sched, time


class FeedbackBar:
    red_part_length = 200
    yellow_part_length = 300
    green_part_length = 200
    lineY_position = 250
    whole_length = red_part_length + yellow_part_length + green_part_length
    line_start_position = 0 - whole_length / 2

    def __init__(self, initial_mark_position):
        self.mark_position = initial_mark_position

    def get_line_middle_position(lineStart, lineLength):
        return lineStart + lineLength / 2

    def paint_line_part(self, line_length, position_x, color, canvas):
        line = stimuli.Rectangle(size=(line_length, 10), position=[position_x, self.lineY_position],
                                 colour=color)
        line.plot(canvas)

    def paint_whole_line(self, canvas):
        self.paint_line_part(self.red_part_length, self.line_start_position + self.red_part_length / 2, misc.constants.C_RED, canvas)
        self.paint_line_part(self.yellow_part_length, self.line_start_position + self.red_part_length + self.yellow_part_length / 2 \
                  , misc.constants.C_YELLOW, canvas)
        self.paint_line_part(self.green_part_length, self.line_start_position + self.red_part_length + self.yellow_part_length \
                  + self.green_part_length / 2
                  , misc.constants.C_GREEN, canvas)

        # plot button and mark line on canvas

        markline = stimuli.Rectangle(size=(4, 25),
                                     position=(self.mark_position, self.lineY_position),
                                     colour=misc.constants.C_BLACK)
        markline.plot(canvas)

    def set_mark_position(self, new_position):
        self.mark_position = new_position

    def update_mark_position(self, update):
        if self.mark_position + update > self.line_start_position and \
                self.mark_position + update < self.line_start_position + self.whole_length:
            self.mark_position += update
