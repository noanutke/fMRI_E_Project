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


class stroop:
    exp = None
    folder = 'NewStroop'
    trials_number = 16
    up_key = 0
    down_key = 1


    def __init__(self, develop_mode, start_time, screen_height, screen_width, start_fast, lsl_stream):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time
        self.outlet = lsl_stream
        self.correct_trials = 0


        self.use_develop_mode = develop_mode
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_mode)
        self.exp = control.initialize()
        control.start(self.exp, auto_create_subject_id=start_fast, skip_ready_screen=start_fast)
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
        self.arrows_directory = "./pictures/arrows/"
        self.arrow_pointing_up_file = self.arrows_directory + "arrow_up.png"
        self.arrow_pointing_down_file = self.arrows_directory + "arrow_down.png"
        self.direction_file_converter = {"pointing_up": self.arrow_pointing_up_file, "pointing_down": self.arrow_pointing_down_file}

    def run(self, block, condition, locations, directions):
        self.block = block
        self.condition = condition
        self.is_practice = True if self.condition == "Practice" else False
        if self.is_practice == True:
            self.outlet.push_sample(["startBlock_practice"])
        self.locations = locations
        self.directions = directions
        if block == "cong":
            self.outlet.push_sample(["startBlock_cong"])
        else:
            self.outlet.push_sample(["startBlock_incong"])


        self.run_experiment()



    def run_experiment(self):

        self.exp.data_variable_names = ["time", "location", "direction", "trialType", "response", "rt"\
                                        ,"is success", "is practice", "blockType"]

        for trial_index in range(0, self.trials_number):
            canvas = stimuli.BlankScreen()

            time_delay = 0
            cross = stimuli.FixCross((50, 50), (0, 0), 5)
            time_delay += cross.plot(canvas)
            picture_arrow = stimuli.Picture(self.direction_file_converter[self.directions[trial_index]] \
                                            , position=self.locations_converter[self.locations[trial_index]])


            time_delay += picture_arrow.preload()

            time_delay += picture_arrow.plot(canvas)

            time_delay += canvas.present();

            key, rt = self.game_controller.wait_press([self.up_key, self.down_key], self.duration, process_control_events=False)
            canvas = stimuli.BlankScreen()
            cross = stimuli.FixCross((50, 50), (0, 0), 5)
            time_delay += cross.plot(canvas)
            time_delay += canvas.present();
            if key != None:
                self.outlet.push_sample(["response_" + str(key)])
                self.exp.clock.wait(self.isi + self.duration - rt - time_delay) # wait the rest of the ISI before going on

            else:
                key, rt = self.game_controller.wait_press([self.up_key, self.down_key], self.isi - time_delay,
                                                          process_control_events=False)
                if key != None:
                    self.outlet.push_sample(["response_" + str(key)])


            self.save_trial_data(key, rt, trial_index)
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
        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = str(int(self.correct_trials / self.trials_number * 100))
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))

            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present();

    def save_trial_data(self, key, rt, trial_index):
        is_success = self.is_success(self.directions[trial_index], key)
        self.outlet.push_sample(["isSuccess_" + str(is_success) + "_condition_" + self.block])
        self.exp.data.add([str(datetime.datetime.now()),
                           self.locations[trial_index], self.directions[trial_index], \
                           key, rt, is_success, self.is_practice \
                              ,self.block])

