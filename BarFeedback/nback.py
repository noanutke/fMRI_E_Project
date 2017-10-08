#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from grid import Grid
import pandas as pd


class Nback:
    exp = None
    auditory_key = misc.constants.K_RIGHT
    visual_key = misc.constants.K_LEFT
    n=0


    def __init__(self, develop_mode, use_aversive_sound):
        self.use_aversive_sound = use_aversive_sound
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_mode)
        self.exp = control.initialize()
        control.start(self.exp)


    def run(self, n, stimuli_group):
        self.digit_list = []
        self.positions_list = []
        self.bar_positions_list = []
        self.n = n
        self.init_stimuli(n, stimuli_group)
        self.run_experiment()

    #digit_list = [1,1,1,2,5,3,5,5,7,8,9,10]

    def init_stimuli(self, n, stimuli_group):
        # Assign spreadsheet filename to `file`
        file = 'C:/Users/NOA/fMRI_E_Project/Nback_stimuli_bar_3.10.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse(str(n)+"back-" + stimuli_group)

        number = 1
        for values in df1.values:
            #if number < 2:
            self.digit_list.insert(len(self.digit_list), values[0])
            self.positions_list.insert(len(self.positions_list), Grid.positions_indices[int(values[1])-1])
            if stimuli_group != "c": # we are not in "No stress" condition
                self.bar_positions_list.insert(len(self.digit_list), values[2])
            #number += 1

    def run_experiment(self):

        self.exp.data_variable_names = ["digit", "position", "targetType", "response", "rt", "responseType"]

        n=2
        ISI = 2500
        stimuliDuration = 500
        counter = 0

        feedback_bar = FeedbackBar(0, self.bar_positions_list)
        grid = Grid()
        for position in self.positions_list:
            digit = self.digit_list[counter]
            canvas = stimuli.BlankScreen()
            #target = stimuli.TextLine(text=str(digit), text_size=80)

            target = stimuli.Rectangle((30,30), misc.constants.C_BLACK, 0, None, None, Grid.positions_locations[position])
            audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio_final/" + str(digit) + ".wav")
            audio.preload()
            target.preload()
            target.plot(canvas)
            grid.paint_grid(canvas)
            feedback_bar.paint_whole_line(canvas)
            canvas.present()
            audio.play()
            key, rt = self.exp.keyboard.wait([misc.constants.K_RIGHT], stimuliDuration)
            if key is None:
                # we have waited stimuliDuration so we can remove
                self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                feedback_bar.paint_whole_line(canvas)
                grid.paint_grid(canvas)
                timeToClear = canvas.present()
                timeToUnload = target.unload()
                key, rt = self.exp.keyboard.wait([misc.constants.K_RIGHT], ISI - timeToUnload - timeToClear)
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
                timeToUnload = target.unload()
                self.exp.clock.wait(ISI - timeToUnload - timeToClear)

            self.save_trial_data(key, rt, counter)
            feedback_bar.default_update_mark_position()

            counter += 1

        #control.end(goodbye_text="Thank you very much...", goodbye_delay=2000)

    def save_trial_data(self, key, rt, counter):
        digit = self.digit_list[counter]
        position = self.positions_list[counter]

        if counter < self.n:
            self.exp.data.add([digit, position, None, None, None, None])
            return

        if key == self.auditory_key:
            if digit == self.digit_list[counter - self.n]:
                self.exp.data.add([digit, position, "Auditory", self.auditory_key, rt, "HIT"])
            else:
                self.exp.data.add([digit, position, None, self.auditory_key, rt, "FA"])

        elif key == self.visual_key:
            if position == self.positions_list[counter - self.n]:
                self.exp.data.add([digit, position, "Visual", self.visual_key, rt, "HIT"])
            else:
                self.exp.data.add([digit, position, None, self.visual_key, rt, "FA"])

        else:
            if position == self.positions_list[counter - self.n]:
                self.exp.data.add([digit, position, "Visual", None, None, "MISS"])
            elif digit == self.digit_list[counter - self.n]:
                self.exp.data.add([digit, position, "Auditory", None, None, "MISS"])
            else:
                self.exp.data.add([digit, position, None, None, None, "CR"])

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
