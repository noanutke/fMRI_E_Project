#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division

from expyriment import control, stimuli, io, design, misc

# settings
design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK


class SelfReport:
    position_x = 0
    line_length = 700

    def stress_evaluation_task(self, line_length, y_position, text_start, text_end, exp, canvas, mark_position):
        # make button

        line = stimuli.Rectangle(size=(line_length,3), position=(self.position_x, y_position),
                    colour=misc.constants.C_BLACK)
        line.plot(canvas)
        if mark_position is not None:
            # plot button and mark line on canvas

            markline = stimuli.Rectangle(size=(1,25),
                        position=(mark_position, line.position[1]),
                        colour=misc.constants.C_RED)
            markline.plot(canvas)
        # present stimulus






    def __init__(self, exp, screen_height, screen_width, type, cognitive_load_log, block):
        self.line_length = screen_width - 200
        self.exp = exp
        self.line_positions_y = []
        self.marks_positions = []
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
            self.marks_positions.insert(len(self.marks_positions), None)
            self.write_text(line_text, self.edges_text[index-1], position_y, self.canvas)
            self.paint_line(position_y, line_text[0], line_text[1], exp, self.canvas, None)
            index += 1
        self.canvas.present()
        # wait for mouse or touch screen response

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
                            , self.canvas, self.marks_positions[index])
            index += 1
        self.exp.mouse.show_cursor()
        self.canvas.present()


    def paint_line(self, y_position, text_start, text_end, exp, canvas, mark_position):
        judgment = self.stress_evaluation_task(self.line_length, y_position, text_start, text_end,\
                exp, canvas, mark_position)


    def wait_for_marks(self):
        self.exp.mouse.show_cursor()
        button_done = None
        while True:
            _id, pos, _rt = self.exp.mouse.wait_press()
            # process clicked position position

            if button_done != None and self.is_done(button_done[0], pos):
                self.exp.mouse.hide_cursor()
                return self.marks_positions
            line_index = 0
            for y_position in self.line_positions_y:
                mark_position = self.check_if_mouse_on_line(y_position, pos)
                if mark_position != None:
                    self.marks_positions[line_index] = mark_position
                    if self.are_all_marked():
                        button_done = self.add_done_button()

                    self.paint_all_lines(button_done)
                    break
                line_index += 1


    def check_if_mouse_on_line(self, y_position, mark_position):
        if abs(mark_position[1] - y_position) <= 50 and \
                              abs(mark_position[0] - self.position_x) <= self.line_length // 2:
            return mark_position[0]
        else:
            return None

    def are_all_marked(self):
        for mark_position in self.marks_positions:
            if mark_position == None:
                return False
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
        for position in self.marks_positions:
            precentage_array.insert(index, (position - line_start) / self.line_length * 100)
            index += 1
        return precentage_array
