#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
import datetime
import time as Time
from expyriment import stimuli, io, design, misc

design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK


class SelfReport:
    position_x = 0
    line_index = 0

    marker_distance_from_scale = 16
    marker_width = 6
    marker_height = 22
    title_distance_from_scale = 40
    edges_distance_above_scale = 20
    start_text_distance_from_scale = -60
    end_text_distance_from_Scale = 50
    text_size = 40
    min_movement_for_update = 1 #to prevent over sensitivity of joystick we only update marker if the
                                # movement is bigger than this value
    increase_movement_speed_by = 10
    wait_for_updates_cycle = 10 #for how long we should wait for input before checking the input status (mili seconds)
    wait_after_button_click = 200 #For how long we should wait after a button click before enabling new input
                                    #from joystick, to prevent over sensitivity of joystick

    # text for load evaluation scales edges
    loadEdgesText = [[u"ךומנ", u"הובג"], [u"ךומנ", u"הובג"], [u"ךומנ", u"הובג"], \
                          [u"הובג", u"ךומנ"], [u"ךומנ", u"הובג"], [u"ךומנ", u"הובג"]]
    # text for load evaluation scales titles
    loadTitleText = [u" ילטנמ סמוע", u"יזיפ סמוע", \
                          u"ןמזמ רזגנה סמוע", u"םיעוציב תמר", \
                          u"ץמאמ", u"לוכסת"]

    # text for stress evaluation scales edges
    stressEdgesText = [[u"אל ללכ", u"דואמ"], \
                            [u"אל ללכ", u"דואמ"], [u"אל ללכ", u"דואמ"]]
    # text for stress evaluation scales titles
    stressTitleText = [u"שח התא ץוחל המכ", \
                            u"שח התא םיענ אל המכ"]

    def __init__(self, exp, screen_height, screen_width, type, cognitive_load_log, outlet, subNumber, \
                 order, task):

        self.cognitive_load_log = cognitive_load_log;
        self.task = task
        self.subNumber = subNumber;
        self.order = order;
        self.task = task;
        self.screen_height = screen_height - 300
        self.screen_width = screen_width
        self.outlet = outlet    #LSL stream

        self.line_length = self.screen_width*0.5
        self.line_start = 0 - self.line_length / 2
        self.line_end = 0 + self.line_length / 2
        self.exp = exp

        self.text_array = []
        self.edges_text = []
        self.line_positions_y = []
        self.old_marks_positions = []
        self.new_marks_positions = []

        self.highest_height = 0 + self.screen_height / 2

        if type == "stress":
            self.text_array = self.stressTitleText
            self.edges_text = self.stressEdgesText
            self.wait_for_miliseconds = 9000

        else:
            self.text_array = self.loadTitleText
            self.edges_text = self.loadEdgesText
            self.wait_for_miliseconds = 20000   # we wait only 20 seconds because due to different delays the
                                                # actual duration is 21 seconds

        self.number_of_lines = len(self.text_array)

        # create array to hold all line positions
        spaces = self.screen_height / (self.number_of_lines + 1)
        index = 1;
        for line_text in self.text_array:
            position_y = self.highest_height - spaces * index
            self.line_positions_y.insert(len(self.line_positions_y), position_y)
            self.new_marks_positions.insert(len(self.new_marks_positions), 0)
            self.old_marks_positions.insert(len(self.old_marks_positions), 0)
            index += 1;

        self.paint_all_lines();

        # wait for responses
        self.outlet.push_sample(["eval_task_" + task + "_start_1_" + type + "_1"])
        self.wait_for_marks()
        self.outlet.push_sample(["eval_task_" + task + "_end_1_" + type + "_1"])

        self.save_current_evaluation_to_file();

    def save_current_evaluation_to_file(self):
        row_to_insert = self.get_positions_array_in_precentage()

        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        row_to_insert.insert(0, self.order)
        row_to_insert.insert(0, current_hour + current_min)
        row_to_insert.insert(0, self.subNumber)
        row_to_insert.insert(0, self.task)
        self.cognitive_load_log.add_row(row_to_insert)

    def paint_all_lines(self):
        self.canvas = stimuli.BlankScreen()

        index = 0
        for line_text in self.text_array:
            y_position = self.line_positions_y[index]
            self.write_text(line_text, self.edges_text[index], y_position, self.canvas)
            self.paint_line(y_position, self.canvas, self.new_marks_positions[index])
            index += 1
        self.canvas.present()
        self.old_marks_positions = self.new_marks_positions

    def update_line(self, y_position, mark_position):
        delay = 0
        markline = stimuli.Rectangle(size=(self.marker_width,self.marker_height),
                    position=(mark_position, y_position+self.marker_distance_from_scale),
                    colour=misc.constants.C_RED)
        delay += markline.plot(self.canvas)
        cover =  stimuli.Rectangle(size=(self.marker_width,self.marker_height),
                    position=(self.old_marks_positions[self.line_index], y_position+self.marker_distance_from_scale),
                    colour=misc.constants.C_GREY)
        delay += cover.plot(self.canvas)
        delay += self.canvas.present()
        self.old_marks_positions[self.line_index] = mark_position
        return delay


    def paint_line(self, y_position, canvas, mark_position):

        line = stimuli.Rectangle(size=(self.line_length,3), position=(self.position_x, y_position),
                    colour=misc.constants.C_BLACK)
        line.plot(canvas)
        if mark_position is not None:


            markline = stimuli.Rectangle(size=(self.marker_width,self.marker_height),
                        position=(mark_position, line.position[1]+self.marker_distance_from_scale),
                        colour=misc.constants.C_RED)
            markline.plot(canvas)


    def wait_for_marks(self):
        # initialize joystick input
        joystick = io.GamePad(0, True, True)
        while self.wait_for_miliseconds > self.wait_for_updates_cycle:

            button, rt = joystick.wait_press(duration=self.wait_for_updates_cycle)

            axis_X = joystick.get_axis(0)

            # decrease the waiting time left for this questionnaire by the time we have waited for input
            if rt == None:
                rt = self.wait_for_updates_cycle
            self.wait_for_miliseconds -= rt;

            self.update_active_scale_if_needed(button)

            self.update_marker_location_if_needed(axis_X)

            self.update_line_if_needed()

    def update_line_if_needed(self):
        if abs(self.new_marks_positions[self.line_index] - \
               self.old_marks_positions[self.line_index]) > self.min_movement_for_update:
            delay = self.update_line(self.line_positions_y[self.line_index], \
                                     self.new_marks_positions[self.line_index])
            self.wait_for_miliseconds -= delay

    def update_active_scale_if_needed(self, button):
        if button != None:  # input was a click button
            self.exp.clock.wait(self.wait_after_button_click)  # wait to decrease joystick sensitivity
            self.wait_for_miliseconds -= self.wait_after_button_click;
        if button != None and self.line_index < len(self.new_marks_positions) - 1:
            self.line_index += 1;
        elif button != None:
            self.line_index = 0;

    def update_marker_location_if_needed(self, axis_X):
        if abs(axis_X) > self.min_movement_for_update:
            if self.new_marks_positions[self.line_index] + axis_X * self.increase_movement_speed_by \
                    >= self.line_end:
                self.new_marks_positions[self.line_index] = self.line_end - 1;
            if self.new_marks_positions[self.line_index] + axis_X * self.increase_movement_speed_by \
                    <= self.line_start:
                self.new_marks_positions[self.line_index] = self.line_start + 1;
            else:
                self.new_marks_positions[self.line_index] += axis_X * self.increase_movement_speed_by;

    def write_text(self, text_above, text_edges, y_position, canvas):
        line_start = 0 - (self.line_length / 2)
        line_end = 0 + (self.line_length / 2)
        text_above = stimuli.TextLine(text_above, [0-10, y_position + self.title_distance_from_scale],\
                                      text_font='Monospace', text_size=self.text_size)
        text_start = stimuli.TextLine(text_edges[0], [line_start + self.start_text_distance_from_scale,\
                                                      y_position + self.edges_distance_above_scale],\
                                      text_font='Monospace', text_size=self.text_size)
        text_end = stimuli.TextLine(text_edges[1], [line_end + self.end_text_distance_from_Scale,\
                                                    y_position + self.edges_distance_above_scale ],\
                                    text_font='Monospace', text_size=self.text_size)
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
