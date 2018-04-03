#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from alarmButtons import AlarmButtons
from grid import Grid
import datetime
import pandas as pd
import random
import numpy
import time


class stroop:
    exp = None
    folder = 'NewStroop'
    test_trials_number = 16
    practice_trials_number = 8
    up_key = 1
    down_key = 0
    port = None;

    def __init__(self, exp, start_time, screen_height, screen_width, start_fast, lsl_stream, subNumber):
        self.subNumber = subNumber;
        self.order = ""
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time
        self.outlet = lsl_stream
        self.correct_trials = 0
        self.exp = exp


        self.game_controller = io.GamePad(0, True, True)
        self.words = []
        self.colors = []
        self.conditions = []
        self.wordsEnglish = []
        self.isi = 1500
        self.duration = 1500
        self.block = ""
        self.is_practice = False
        self.directions = []
        self.locations = []
        self.locations_converter = {"up": [0,200], "down": [0, -200]}
        self.blockIndex = 0
        self.arrows_directory = "./pictures/arrows/"
        self.arrow_pointing_up_file = self.arrows_directory + "arrow_up.png"
        self.arrow_pointing_down_file = self.arrows_directory + "arrow_down.png"
        self.direction_file_converter = {"pointing_up": self.arrow_pointing_up_file, "pointing_down": self.arrow_pointing_down_file}

    def run(self, block, condition, locations, directions, order, port, block_index=0):
        self.blockIndex = block_index
        self.correct_trials = 0
        self.order = order
        self.block = block
        self.condition = condition
        self.is_practice = True if self.condition == "practice" else False
        self.port = port
        self.locations = locations
        self.directions = directions

        self.outlet.push_sample(["sp_p" + ("1" if self.is_practice else "0") \
                                 + "_c" + ("1" if "cong" in self.block else "0") \
                                 + "_o" + self.order \
                                 + "_s" + self.subNumber + "_bi" + str(block_index+1)])
        self.run_experiment()



    def run_experiment(self):

        self.exp.data_variable_names = ["time", "location", "direction", "trialType", "response", "rt"\
                                        ,"is success", "is practice", "blockType", "order"]
        start_block_time = time.time()
        currentTrailsNumber = self.test_trials_number;
        if self.is_practice:
            currentTrailsNumber = self.practice_trials_number;
        for trial_index in range(0, currentTrailsNumber):
            canvas = stimuli.BlankScreen()
            start_trial_time = time.time()
            time_delay = 0
            cross = stimuli.FixCross((50, 50), (0, 0), 5)
            time_delay += cross.plot(canvas)
            picture_arrow = stimuli.Picture(self.direction_file_converter[self.directions[trial_index]] \
                                            , position=self.locations_converter[self.locations[trial_index]])


            time_delay += picture_arrow.preload()

            time_delay += picture_arrow.plot(canvas)

            time_delay += canvas.present();

            self.outlet.push_sample(["sp_arr_" + ("u" if "up" in self.directions[trial_index] else "d") \
                                    + "_"  + ("u" if "up" in self.locations[trial_index] else "d")])

            key, rt = self.game_controller.wait_press([self.up_key, self.down_key], self.duration, process_control_events=False)
            canvas = stimuli.BlankScreen()
            cross = stimuli.FixCross((50, 50), (0, 0), 5)

            if key != None:
                picture_arrow = stimuli.Picture(self.direction_file_converter[self.directions[trial_index]] \
                                                , position=self.locations_converter[self.locations[trial_index]])

                time_delay += picture_arrow.preload()
                time_delay += picture_arrow.plot(canvas)
                time_delay += cross.plot(canvas)
                time_delay += canvas.present()
                self.port.setData(int(50))
                self.outlet.push_sample(["sp_k_" + str(key)])
                self.exp.clock.wait(self.duration - rt) # wait the rest of the ISI before going on

                canvas = stimuli.BlankScreen()
                cross = stimuli.FixCross((50, 50), (0, 0), 5)
                time_delay += cross.plot(canvas)
                time_delay += canvas.present()
                self.exp.clock.wait(
                    self.isi - time_delay)  # wait the rest of the ISI before going on

            else:
                canvas = stimuli.BlankScreen()
                cross = stimuli.FixCross((50, 50), (0, 0), 5)
                time_delay += cross.plot(canvas)
                time_delay += canvas.present()
                key, rt = self.game_controller.wait_press([self.up_key, self.down_key], self.isi - time_delay,
                                                          process_control_events=False)
                if key != None:
                    self.exp.clock.wait(
                        self.isi - rt - time_delay)  # wait the rest of the ISI before going on

                self.outlet.push_sample(["sp_k_" + str(key)])


            self.save_trial_data(key, rt, trial_index)

        end_trial_time = time.time()
        print('n')
        self.show_feedback_if_needed()

    def is_success(self, direction, response_key):
        if response_key == self.up_key and direction == "pointing_up":
            self.correct_trials += 1
            return True
        elif response_key == self.down_key and direction == "pointing_down":
            self.correct_trials += 1
            return True
        else:
            return False

    def show_feedback_if_needed(self):
        currentTrailsNumber = self.test_trials_number;
        if self.is_practice:
            currentTrailsNumber = self.practice_trials_number;
        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = str(float(self.correct_trials) / currentTrailsNumber * 100)
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))

            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present();

    def save_trial_data(self, key, rt, trial_index):
        is_success = self.is_success(self.directions[trial_index], key)
        self.outlet.push_sample(["sp_res_" + ("1" if is_success else "0")])
        self.exp.data.add([str(datetime.datetime.now()),
                           self.locations[trial_index], self.directions[trial_index], \
                           key, rt, is_success, self.is_practice \
                              ,self.block, self.order])


