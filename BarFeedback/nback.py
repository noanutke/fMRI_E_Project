#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from grid import Grid
import datetime
import pandas as pd


class Nback:
    exp = None
    single_target = misc.constants.K_RIGHT
    dual_target = misc.constants.K_LEFT
    n=0


    def __init__(self, develop_mode, use_aversive_sound):
        self.use_aversive_sound = use_aversive_sound
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_mode)
        self.exp = control.initialize()
        control.start(self.exp)
        self.digit = None
        self.position = None
        self.is_practice = False
        self.correct_trials = 0
        self.trials_number = 0


    def run(self, n, stimuli_group, stimuli_type="both"):
        self.digit_list = []
        self.positions_list = []
        self.bar_positions_list = []
        self.n = n
        self.digit = None
        self.position = None
        self.position_text = None
        self.init_stimuli(n, stimuli_group, stimuli_type)
        self.is_practice = True if stimuli_group == 'p' else False
        self.run_experiment()

    #digit_list = [1,1,1,2,5,3,5,5,7,8,9,10]

    def init_stimuli(self, n, stimuli_group, stimuli_type="both"):
        # Assign spreadsheet filename to `file`
        file = 'C:/Users/NOA/fMRI_E_Project/Nback_stimuli_bar_3.10.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse(str(n) + "back-" + stimuli_group)

        number = 0
        for values in df1.values:
            #if number > 2:
               #break
            if stimuli_type == 'a' or stimuli_type == "both":
                self.digit_list.insert(len(self.digit_list), values[0])
            if stimuli_type == 'v' or stimuli_type == "both":
                self.positions_list.insert(len(self.positions_list), Grid.positions_indices[int(values[1])-1])
            if stimuli_group != "c" and stimuli_group != 'p': # we are not in "No stress" condition or in practice
                self.bar_positions_list.insert(len(self.digit_list), values[2])

            self.trials_number += 1
            number += 1


    def run_experiment(self):

        self.exp.data_variable_names = ["time", "digit", "position", "targetType", "response", "rt",\
                                        "responseType"]

        n=2
        ISI = 2500
        stimuliDuration = 500
        trials_number = len(self.positions_list) if len(self.positions_list) > 0 else len(self.digit_list)

        feedback_bar = FeedbackBar(0, self.bar_positions_list)

        grid = Grid(len(self.positions_list))

        for trial in range(trials_number):
            target = None
            if len(self.digit_list) > 0:
                self.digit = self.digit_list[trial]
                audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio_final/" + str(self.digit) + ".wav")
                audio.preload()
            canvas = stimuli.BlankScreen()
            #target = stimuli.TextLine(text=str(digit), text_size=80)

            if len(self.positions_list) > 0:
                self.position_text = self.positions_list[trial]
                self.position = Grid.positions_locations[self.position_text]
                target = stimuli.Rectangle((30,30), misc.constants.C_BLACK, 0, None, None, self.position)
                target.preload()
                target.plot(canvas)
                grid.paint_grid(canvas)

            feedback_bar.paint_whole_line(canvas)
            canvas.present()
            if self.digit != None:
                audio.play()

            key, rt = self.exp.keyboard.wait([self.single_target, self.dual_target], stimuliDuration)
            if key is None:
                # we have waited stimuliDuration so we can remove
                self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                feedback_bar.paint_whole_line(canvas)
                grid.paint_grid(canvas)
                timeToClear = canvas.present()
                timeToUnload = 0
                if target != None:
                    timeToUnload = target.unload()
                key, rt = self.exp.keyboard.wait([self.single_target, self.dual_target], ISI - timeToUnload - timeToClear)
                if key:
                    self.exp.clock.wait(ISI - rt) # wait the rest of the ISI before going on
                    rt = rt + stimuliDuration
            else:
                self.exp.clock.wait(stimuliDuration - rt) # wait the rest of the stimuliDuration before removing
                # we have now waited stimuliDuration so we can remove
                self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                feedback_bar.paint_whole_line(canvas)
                grid.paint_grid(canvas)
                timeToClear = canvas.present()
                if target != None:
                    timeToUnload = target.unload()
                self.exp.clock.wait(ISI - timeToUnload - timeToClear)

            self.save_trial_data(key, rt, trial)
            feedback_bar.default_update_mark_position()

        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = str(int(self.correct_trials / self.trials_number * 100))
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))
            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present()
        #control.end(goodbye_text="T:hank you very much...", goodbye_delay=2000)

    def save_trial_data(self, key, rt, counter):
        if counter < self.n:
            self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, None, None, None])
            self.correct_trials += 1
            return

        if key == self.single_target:
            if self.digit != None and self.digit == self.digit_list[counter - self.n]:
                if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                    self.exp.data.add([str(datetime.datetime.now()),
                        self.digit, self.position_text, "Dual", self.single_target, rt, "Wrong Response"])
                else:
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Auditory", self.single_target, rt,\
                                      "Correct Response"])
                    self.correct_trials += 1
            elif self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Visual", self.single_target, rt, "Correct Response"])
                self.correct_trials += 1
            else:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, self.single_target, rt, "FA"])

        elif key == self.dual_target:
            if self.digit != None and self.digit == self.digit_list[counter - self.n] and \
                self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "Dual", self.dual_target, rt, "Correct Response"])
                self.correct_trials += 1
            elif self.digit != None and self.digit == self.digit_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Auditory", self.dual_target, rt, \
                                   "Wrong Response"])

            elif self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "Visual", self.dual_target, rt, "Wrong Response"])
            else:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "None", self.dual_target, rt, "FA"])

        else:
            if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Visual", None, None, "MISS"])
            elif self.digit != None and self.digit == self.digit_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Auditory", None, None, "MISS"])
            else:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, None, None, "Correct Rejection"])
                self.correct_trials += 1

    def play_aversive_sound_if_needed(self, feedback_bar):
        if self.use_aversive_sound == False or feedback_bar.is_feedback_bar_on() == False:
            return
        audio = None
        feedback_bar.update_trials_in_danger()
        if feedback_bar.is_aversive_stimuli_fade_in():
            audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio_final/Alarm_-12db.wav")
        elif feedback_bar.is_aversive_stimuli_fade_out():
            audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio_final/Alarm_-12db.wav")
        elif feedback_bar.is_aversive_stimuli_full():
            audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio_final/Alarm_-12db.wav")
        if audio != None:
            audio.preload()
            audio.play()
