#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
import datetime
import time as Time
from expyriment import control, stimuli, io, design, misc
import copy
import time
#from psychopy import parallel

# settings
design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK



class SelfReport:
    position_x = 0
    line_length = 700
    line_index = 0


    def __init__(self, exp, screen_height, screen_width, type, cognitive_load_log, block, outlet, subNumber, \
                 order, task):

        self.task = task;
        self.screen_height = screen_height - 300
        self.screen_width = screen_width
        self.outlet = outlet

        self.line_length = self.screen_width*0.5
        self.line_start = 0 - self.line_length / 2
        self.line_end = 0 + self.line_length / 2
        self.exp = exp
        self.line_positions_y = []
        self.old_marks_positions = []
        self.new_marks_positions = []
        self.lines_updates = []

        self.lowest_height = 0 - self.screen_height/2
        self.highest_height = 0 + self.screen_height / 2


        self.canvas = stimuli.BlankScreen()
        self.loadEdgedText =  [[u"ךומנ", u"הובג"], [u"ךומנ", u"הובג"], [ u"ךומנ",u"הובג" ], \
                                           [u"הובג",u"ךומנ"], [u"ךומנ",u"הובג"], [u"ךומנ",u"הובג"]]
        self.loadTitleText = [u" ילטנמ סמוע",u"יזיפ סמוע", \
                                          u"ןמזמ רזגנה סמוע",u"םיעוציב תמר", \
                                          u"ץמאמ",u"לוכסת"]
        self.stressEdgesText = [[u"אל ללכ",u"דואמ"], \
                                    [u"אל ללכ",u"דואמ"], [u"אל ללכ",u"דואמ"]]
        self.stressTitleText = [u"שח התא ץוחל המכ",\
                                   u"שח התא םיענ אל המכ"]
        self.wait_for_miliseconds = 3000
        self.text_array = []
        self.edges_text = []

        if type == "stress":
            self.text_array = self.stressTitleText
            self.edges_text = self.stressEdgesText
            self.wait_for_miliseconds = 9000

        else:
            self.text_array = self.loadTitleText
            self.edges_text = self.loadEdgedText
            self.wait_for_miliseconds = 20000

        self.number_of_lines = len(self.text_array)
        spaces = self.screen_height / (self.number_of_lines + 1)

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

        start_block_time = Time.time()
        self.outlet.push_sample(["eval_task_" + task + "_start_1_type_" + type])
        self.wait_for_marks()
        end_block_time = Time.time()
        print('noa')
        self.outlet.push_sample(["eval_task_" + task + "_end_1_type_" + type])
        row_to_insert = self.get_positions_array_in_precentage()
        time = datetime.datetime.now()
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        row_to_insert.insert(0, order)
        row_to_insert.insert(0, current_hour + current_min)
        row_to_insert.insert(0, subNumber)
        row_to_insert.insert(0, task)
        cognitive_load_log.add_row(row_to_insert)
        end_block_time = Time.time()
        print('noa')


    def paint_all_lines(self):
        self.canvas = stimuli.BlankScreen()

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
        delay = 0
        markline = stimuli.Rectangle(size=(6,22),
                    position=(mark_position, y_position+16),
                    colour=misc.constants.C_RED)
        delay += markline.plot(self.canvas)
        cover =  stimuli.Rectangle(size=(6,22),
                    position=(self.old_marks_positions[self.line_index], y_position+16),
                    colour=misc.constants.C_GREY)
        delay += cover.plot(self.canvas)
        delay += self.canvas.present()
        self.old_marks_positions[self.line_index] = mark_position
        return delay



    def paint_line(self, y_position, text_start, text_end, exp, canvas, mark_position):

        line = stimuli.Rectangle(size=(self.line_length,3), position=(self.position_x, y_position),
                    colour=misc.constants.C_BLACK)
        line.plot(canvas)
        if mark_position is not None:


            markline = stimuli.Rectangle(size=(6,22),
                        position=(mark_position, line.position[1]+16),
                        colour=misc.constants.C_RED)
            markline.plot(canvas)


    def wait_for_marks(self):
        game1 = io.GamePad(0, True, True)
        while self.wait_for_miliseconds > 5:



            button, rt = game1.wait_press(duration=10)
            #key, rt = self.exp.keyboard.wait([misc.constants.K_1, misc.constants.K_2, misc.constants.K_4],\
                                             #self.wait_for_miliseconds)
            axis0 = 0
            axis0 = game1.get_axis(0)


            if rt == None:
                rt = 10
            self.wait_for_miliseconds -= rt;
            # process clicked position position

            if button != None:
                self.exp.clock.wait(200)
                self.wait_for_miliseconds -= 200;
            if button != None and self.line_index < len(self.new_marks_positions)-1:
                self.line_index += 1;
            elif button != None :
                self.line_index = 0;
            elif button != None  and self.line_index == len(self.new_marks_positions)-1:
                continue;



            if abs(axis0) > 0.1:
                if self.new_marks_positions[self.line_index] + axis0*10 >= self.line_end:
                    self.new_marks_positions[self.line_index] = self.line_end - 1;
                if self.new_marks_positions[self.line_index] + axis0*10 <= self.line_start:
                    self.new_marks_positions[self.line_index] = self.line_start + 1;
                else:
                    self.new_marks_positions[self.line_index] += axis0*10;

            if abs(self.new_marks_positions[self.line_index] - \
            self.old_marks_positions[self.line_index]) > 1:

                delay = self.update_line(self.line_positions_y[self.line_index], \
                                 self.new_marks_positions[self.line_index])
                self.wait_for_miliseconds -= delay

    def check_if_mouse_on_line(self, y_position, mark_position):
        if abs(mark_position[1] - y_position) <= 50 and \
                              abs(mark_position[0] - self.position_x) <= self.line_length // 2:
            return mark_position[0]
        else:
            return None


    def write_text(self, text_above, text_edges, y_position, canvas):
        line_start = 0 - (self.line_length / 2)
        line_end = 0 + (self.line_length / 2)
        text_above = stimuli.TextLine(text_above, [0-10, y_position + 40], text_font='Monospace', text_size=40)
        text_start = stimuli.TextLine(text_edges[0], [line_start - 60, y_position + 20], text_font='Monospace', text_size=40)
        text_end = stimuli.TextLine(text_edges[1], [line_end + 50, y_position + 20 ], text_font='Monospace', text_size=40)
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
