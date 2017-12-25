#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from alarmButtons import AlarmButtons
from grid import Grid
import datetime
import pandas as pd
import random


class stroop:
    exp = None
    folder = 'NewStroop'
    trials_number = 16
    yellow_key = misc.constants.K_1
    green_key = misc.constants.K_2
    blue_key = misc.constants.K_3
    red_key = misc.constants.K_4


    def __init__(self, develop_mode, start_time, screen_height, screen_width, start_fast, use_bar):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time

        self.use_develop_mode = develop_mode
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_mode)
        self.exp = control.initialize()
        control.start(self.exp, auto_create_subject_id=start_fast, skip_ready_screen=start_fast)
        self.words = []
        self.colors = []
        self.conditions = []
        self.wordsEnglish = []
        self.isi = 1500
        self.duration = 1500
        self.block = ""
        self.is_practice = False

    def run(self, block):
        self.block = block
        self.is_practice = True if self.block == "p" else False
        self.init_stimuli(block)
        if block == "high":
            self.isi = 2500
            self.duration = 500
        elif block == "medium":
            self.isi = 2000
            self.duration = 1000

        self.run_experiment()


    def from_english_word_to_hebrew(self, word):
        if word =="red":
            return u"אדום"
        elif word == u"blue":
            return u"כחול"
        elif word == "green":
            return u"ירוק"
        else:
            return u"צהוב"

    def init_stimuli(self, block):
        # Assign spreadsheet filename to `file`
        file = '../' + self.folder + '/' + block + '.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse('Sheet1')
        tempWords = []
        tempColors = []
        tempConditions = []
        tempWordsEnglish = []
        for values in df1.values:
            tempWords.insert(len(tempWords), values[0])
            tempColors.insert(len(tempColors), values[1])
            tempWordsEnglish.insert(len(tempWordsEnglish), values[2])
            tempConditions.insert(len(tempConditions), values[3])

        indicesList = list(range(0,16));
        random.shuffle(indicesList)
        for index in indicesList:
            self.words.insert(len(self.words), self.from_english_word_to_hebrew(tempWordsEnglish[index]))
            self.colors.insert(len(self.colors), tempColors[index])
            self.wordsEnglish.insert(len(self.wordsEnglish), tempWordsEnglish[index])
            self.conditions.insert(len(self.conditions), tempConditions[index])

        possible_colors = ["red", "green", "blue", "yellow"]
        if self.block == "baseline":
            for index in range(self.trials_number):
                if self.conditions[index] == "incong":
                    color_index = random.randint(0,len(possible_colors)-1)
                    self.colors = possible_colors[color_index]
                    possible_colors.remove(possible_colors[color_index])

    def convert_colors(self, color_string):
        if color_string == "red":
            return misc.constants.C_RED
        elif color_string == "yellow":
            return misc.constants.C_YELLOW
        elif color_string == "blue":
            return misc.constants.C_BLUE
        else:
            return misc.constants.C_GREEN

    def get_word_picture_path(self, word, color):
        return "../NewStroop/words/" + word[0] + color[0] + ".png"

    def run_experiment(self):

        self.exp.data_variable_names = ["time", "word", "color", "trialType", "response", "rt"\
                                        ,"is success", "is practice", "loadLevel"]

        for trial_index in range(0, self.trials_number):
            canvas = stimuli.BlankScreen()
            time_delay = 0
            picture_word = stimuli.Picture(self.get_word_picture_path(self.wordsEnglish[trial_index],\
                                                                      self.colors[trial_index]))
            picture_buttons = stimuli.Picture("../NewStroop/words/buttons.png", position=(0,200))

            time_delay += picture_buttons.preload()
            time_delay += picture_word.preload()
            time_delay += picture_word.plot(canvas)
            time_delay += picture_buttons.plot(canvas)
            time_delay += canvas.present();

            key, rt = self.exp.keyboard.wait([self.yellow_key, self.green_key, self.blue_key, self.red_key]\
                                             , self.duration)
            canvas = stimuli.BlankScreen()
            canvas.present();
            if key:
                self.exp.clock.wait(self.isi + self.duration - rt) # wait the rest of the ISI before going on

            else:
                self.exp.clock.wait(self.isi)

            self.save_trial_data(key, rt, trial_index)

    def is_success(self, word, response_key):
        if response_key == self.red_key and word == "red":
            return True
        elif response_key == self.blue_key and word == "blue":
            return True
        elif response_key == self.green_key and word == "green":
            return True
        elif response_key == self.yellow_key and word == "yellow":
            return True
        else:
            return False

    def save_trial_data(self, key, rt, trial_index):
        self.exp.data.add([str(datetime.datetime.now()),
                           self.words[trial_index], self.colors[trial_index], "Dual", self.conditions[trial_index], \
                           key, rt, self.is_success(self.wordsEnglish[trial_index], key), self.is_practice \
                              ,self.block])

