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

    def __init__(self, develop_model, n, stimuli_group):
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_model)
        self.n = n
        self.digit_list = []
        self.positions_list = []
        self.init_stimuli(n, stimuli_group)



    #digit_list = [1,1,1,2,5,3,5,5,7,8,9,10]

    def init_stimuli(self, n, stimuli_group):
        # Assign spreadsheet filename to `file`
        file = 'C:/Users/NOA/fMRI_E_Project/stimuli_new.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse(str(n)+"back-" + stimuli_group)

        for values in df1.values:
            self.digit_list.insert(len(self.digit_list), values[0])
            self.positions_list.insert(len(self.positions_list), Grid.positions_indices[values[1]-1])

    def run_experiment(self):
        self.exp = control.initialize()

        self.exp.data_variable_names = ["digit", "position", "targetType", "response", "rt", "responseType"]

        control.start(self.exp)
        n=2
        ISI = 1000
        stimuliDuration = 1000
        counter = 0

        feedback_bar = FeedbackBar(10)
        grid = Grid()
        for position in self.positions_list:
            digit = self.digit_list[counter]
            canvas = stimuli.BlankScreen()
            #target = stimuli.TextLine(text=str(digit), text_size=80)

            target = stimuli.Rectangle((30,30), misc.constants.C_BLACK, 0, None, None, Grid.positions_locations[position])
            audio = stimuli.Audio("C:/Users/NOA/fMRI_E_Project/audio/" + str(digit) + ".wav")
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
                canvas = stimuli.BlankScreen()
                feedback_bar.paint_whole_line(canvas)
                grid.paint_grid(canvas)
                timeToClear = canvas.present()
                timeToUnload = target.unload()
                self.exp.clock.wait(ISI - timeToUnload - timeToClear)

            self.save_trial_data(key, rt, counter)
            feedback_bar.default_update_mark_position()

            counter += 1

        control.end(goodbye_text="Thank you very much...", goodbye_delay=2000)

    def save_trial_data(self, key, rt, counter):
        digit = self.digit_list[counter]
        position = self.positions_list[counter]

        if counter < 1:
            self.exp.data.add([digit, position, None, None, None, None])

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
