#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division

from expyriment import control, stimuli, io, design, misc
import copy

# settings
design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK


class SelfReport:
    position_x = 0
    line_length = 700
    line_index = 0


    def __init__(self, exp, screen_height, screen_width, type, cognitive_load_log, block):
        self.line_length = screen_width - 200
        self.line_start = 0 - self.line_length / 2
        self.line_end = 0 + self.line_length / 2
        self.exp = exp
        self.line_positions_y = []
        self.old_marks_positions = []
        self.new_marks_positions = []
        self.lines_updates = []
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.lowest_height = 0 - screen_height/2
        self.highest_height = 0 + screen_height / 2

        self.canvas = stimuli.BlankScreen()
        self.loadEdgedText =  [["Low", "High"], ["Low", "High"], ["Low", "High"], \
                                           ["Good", "Poor"], ["Low", "High"], ["Low", "High"]]
        self.loadTitleText = ["Mental Demand", "Physical Demand", \
                                           "Temporal Demand", "Performance", \
                                           "Effort", "Frustration"]
        self.stressEdgesText = [["not at all", "extremely"], \
                                    ["not at all", "extremely"], ["not at all", "extremely"]]
        self.stressTitleText = ["how stressful do you feel",\
                                    "how unpleasant do you feel"]

        self.text_array = []
        self.edges_text = []
        if type == "stress":
            self.text_array = self.stressTitleText
            self.edges_text = self.stressEdgesText

        else:
            self.text_array = self.loadTitleText
            self.edges_text = self.loadEdgedText

        self.number_of_lines = len(self.text_array)
        spaces = screen_height / (self.number_of_lines + 1)

        index = 1
        for line_text in self.text_array:
            position_y = self.highest_height - spaces * index
            self.line_positions_y.insert(len(self.line_positions_y), position_y)
            self.lines_updates.insert(len(self.lines_updates), None)
            self.new_marks_positions.insert(len(self.new_marks_positions), 0)
            self.old_marks_positions.insert(len(self.old_marks_positions), 0)
            self.write_text(line_text, self.edges_text[index-1], position_y, self.canvas)
            self.paint_line(position_y, line_text[0], line_text[1], exp, self.canvas, 0)
            index += 1
        self.canvas.present()
        # wait for mouse or touch screen response
        self.buttonA = stimuli.Rectangle(size=(80, 40), position=(0, 0 - self.screen_height/2 + 40))
        self.textA = stimuli.TextLine(text="done", position=self.buttonA.position,
                                 text_colour=misc.constants.C_WHITE)
        self.wait_for_marks()
        row_to_insert = self.get_positions_array_in_precentage()
        row_to_insert.insert(0, block)
        cognitive_load_log.add_row(row_to_insert)


    def paint_all_lines(self, button_done):
        self.canvas = stimuli.BlankScreen()
        if button_done != None:
            button_done[0].plot(self.canvas)
            button_done[1].plot(self.canvas)
        index = 0
        for line_text in self.text_array:
            y_position = self.line_positions_y[index]
            self.write_text(line_text, self.edges_text[index], y_position, self.canvas)
            self.paint_line(y_position, line_text[0], line_text[1], self.exp\
                            , self.canvas, self.new_marks_positions[index])
            index += 1
        self.exp.mouse.show_cursor()
        self.canvas.present()
        self.old_marks_positions = self.new_marks_positions

    def update_line(self, y_position, mark_position):
        markline = stimuli.Rectangle(size=(1,25),
                    position=(mark_position, y_position+16),
                    colour=misc.constants.C_RED)
        markline.plot(self.canvas)
        cover =  stimuli.Rectangle(size=(1,25),
                    position=(self.old_marks_positions[self.line_index], y_position+16),
                    colour=misc.constants.C_GREY)
        cover.plot(self.canvas)
        self.canvas.present()
        self.old_marks_positions[self.line_index] = mark_position



    def paint_line(self, y_position, text_start, text_end, exp, canvas, mark_position):
        # make button

        line = stimuli.Rectangle(size=(self.line_length,3), position=(self.position_x, y_position),
                    colour=misc.constants.C_BLACK)
        line.plot(canvas)
        if mark_position is not None:
            # plot button and mark line on canvas

            markline = stimuli.Rectangle(size=(1,25),
                        position=(mark_position, line.position[1]+16),
                        colour=misc.constants.C_RED)
            markline.plot(canvas)


    def wait_for_marks(self):

        button_done = None
        while True:
            key, rt = self.exp.keyboard.wait([misc.constants.K_1, misc.constants.K_2, misc.constants.K_4])
            # process clicked position position

            if key == misc.constants.K_4 and self.line_index == len(self.new_marks_positions)-1 and button_done != None:
                return self.new_marks_positions

            elif key == misc.constants.K_4 and self.line_index < len(self.new_marks_positions)-1:
                self.line_index += 1;
            elif key == misc.constants.K_4:
                self.line_index = 0;
            elif key == misc.constants.K_4 and self.line_index == len(self.new_marks_positions)-1:
                continue;

            if key == misc.constants.K_1:
                self.lines_updates[self.line_index] = True;
                while True:
                    key2, rt2 = self.exp.keyboard.wait(None, 50, True)
                    if rt2 != None or key2 == misc.constants.K_1:
                        break
                    if self.new_marks_positions[self.line_index] <= self.line_start:
                        break
                    self.new_marks_positions[self.line_index] -= 5;
                    if self.are_all_marked():
                        button_done = self.add_done_button()
                    self.update_line(self.line_positions_y[self.line_index], \
                                     self.new_marks_positions[self.line_index])

            if key == misc.constants.K_2:
                self.lines_updates[self.line_index] = True;
                while True:
                    key2, rt2 = self.exp.keyboard.wait(None, 50, True)
                    if rt2 != None or  key2 == misc.constants.K_2:
                        break
                    if self.new_marks_positions[self.line_index] >= self.line_end:
                        break
                    self.new_marks_positions[self.line_index] += 5;
                    if self.are_all_marked():
                        button_done = self.add_done_button()
                    self.update_line(self.line_positions_y[self.line_index], \
                                     self.new_marks_positions[self.line_index])









    def check_if_mouse_on_line(self, y_position, mark_position):
        if abs(mark_position[1] - y_position) <= 50 and \
                              abs(mark_position[0] - self.position_x) <= self.line_length // 2:
            return mark_position[0]
        else:
            return None

    def are_all_marked(self):
        for update in self.lines_updates:
            if update == None:
                return False

        self.buttonA.plot(self.canvas)
        self.textA.plot(self.canvas)
        return True

    def is_done(self, button, position):
        if button.overlapping_with_position(position):
            return True
        return False

    def add_done_button(self):
        buttonA = stimuli.Rectangle(size=(80, 40), position=(0, 0 - self.screen_height/2 + 40))
        textA = stimuli.TextLine(text="done", position=buttonA.position,
                                 text_colour=misc.constants.C_WHITE)

        return [buttonA, textA]

    def write_text(self, text_above, text_edges, y_position, canvas):
        line_start = 0 - (self.line_length / 2)
        line_end = 0 + (self.line_length / 2)
        text_above = stimuli.TextLine(text_above, [0-10, y_position + 40])
        text_start = stimuli.TextLine(text_edges[0], [line_start - 30, y_position + 20])
        text_end = stimuli.TextLine(text_edges[1], [line_end, y_position + 20 ])
        text_above.plot(canvas)
        text_start.plot(canvas)
        text_end.plot(canvas)

    def get_positions_array_in_precentage(self):
        precentage_array = []
        line_start = 0 - (self.line_length / 2)
        index = 0
        for position in self.new_marks_positions:
            precentage_array.insert(index, (position - line_start) / self.line_length * 100)
            index += 1
        return precentage_array
