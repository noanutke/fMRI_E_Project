#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from alarmButtons import AlarmButtons
from grid import Grid
import datetime
import pandas as pd
import random


class Nback:
    exp = None
    single_target = misc.constants.K_RIGHT
    dual_target = misc.constants.K_LEFT
    n=0


    def __init__(self, develop_mode, start_time, screen_height, screen_width, start_fast, use_bar):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time
        self.use_aversive_sound = False
        self.stress_condition = ""
        self.use_develop_mode = develop_mode
        design.defaults.experiment_background_colour = misc.constants.C_GREY
        design.defaults.experiment_foreground_colour = misc.constants.C_BLACK
        control.set_develop_mode(develop_mode)
        self.exp = control.initialize()
        control.start(self.exp, auto_create_subject_id=start_fast, skip_ready_screen=start_fast)
        self.digit = None
        self.position = None
        self.is_practice = False
        self.is_dual_practice = False
        self.correct_trials = 0
        self.hit_trials = 0
        self.rt_practice = 0
        self.trials_number = 0
        self.last_trial_error = False
        self.last_trial_rt = None
        self.show_alarms = False
        self.use_bar = use_bar

    def ask_for_parameters(self):
        canvas = stimuli.BlankScreen()
        auditory_first = stimuli.Rectangle(size=(100, 80), position=(150, 0))
        text_auditory_first = stimuli.TextLine(text="Auditory First", position=auditory_first.position,
                                 text_colour=misc.constants.C_WHITE)
        sensory_first = stimuli.Rectangle(size=(100, 80), position=(-150, 0))
        text_sensory_first = stimuli.TextLine(text="Sensory First", position=sensory_first.position,
                                 text_colour=misc.constants.C_WHITE)

        test_mode = stimuli.Rectangle(size=(100, 80), position=(0, -150))
        text_test_mode = stimuli.TextLine(text="Test Mode", position=test_mode.position,
                                 text_colour=misc.constants.C_WHITE)

        auditory_first.plot(canvas)
        text_auditory_first.plot(canvas)

        sensory_first.plot(canvas)
        text_sensory_first.plot(canvas)

        test_mode.plot(canvas)
        text_test_mode.plot(canvas)

        self.exp.mouse.show_cursor()
        canvas.present()

        while True:
            _id, pos, _rt = self.exp.mouse.wait_press()

            if sensory_first.overlapping_with_position(pos):
                self.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'pain'
            elif auditory_first.overlapping_with_position(pos):
                self.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'sound'
            elif test_mode.overlapping_with_position(pos):
                self.exp.mouse.hide_cursor()
                self.use_develop_mode = True
                return 'sound'

    def run(self, n, stimuli_group, stimuli_type="both"):
        self.trials_number = 0
        self.correct_trials = 0
        self.hit_trials = 0
        self.digit_list = []
        self.positions_list = []
        self.alarms_order_list = []
        self.n = n
        self.digit = None
        self.position = None
        self.position_text = None
        self.init_stimuli(n, stimuli_group, stimuli_type)
        self.show_alarms = True if stimuli_group != 'p' and stimuli_group != 'c' else False
        self.is_practice = True if stimuli_group == 'p' else False
        self.is_dual_practice = True if stimuli_group == 'p' and stimuli_type == 'both' else False
        if self.is_practice == True:
            self.rt_practice = 0
        if stimuli_group == 'a':
            self.use_aversive_sound = True
            self.stress_condition = "sound"
        elif stimuli_group == 'b':
            self.stress_condition = "pain"
            self.use_aversive_sound = False
        else:
            self.stress_condition = "no"
            self.use_aversive_sound = False

        self.last_trial_error = False
        self.run_experiment()

    #digit_list = [1,1,1,2,5,3,5,5,7,8,9,10]

    def init_stimuli(self, n, stimuli_group, stimuli_type="both"):
        # Assign spreadsheet filename to `file`
        file = './Nback_stimuli_bar_3.10.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse(str(n) + "back-" + stimuli_group)

        number = 0
        for values in df1.values:
            if number > 0:
               break
            if stimuli_type == 'a' or stimuli_type == "both":
                self.digit_list.insert(len(self.digit_list), values[0])
            if stimuli_type == 'v' or stimuli_type == "both":
                self.positions_list.insert(len(self.positions_list), Grid.positions_indices[int(values[1])-1])
            if stimuli_group != "c" and stimuli_group != 'p': # we are not in "No stress" condition or in practice
                self.alarms_order_list.insert(len(self.digit_list), values[3])

            self.trials_number += 1
            if self.use_develop_mode == True:
                number += 1


    def run_experiment(self):

        self.exp.data_variable_names = ["time", "digit", "position", "targetType", "response", "rt",\
                                        "responseType", "is success", "n", "stress condition", "is practice",\
                                        "perfLevel", "alarmPlayed"]

        n=2
        ISI = 2500
        stimuliDuration = 500
        trials_number = len(self.positions_list) if len(self.positions_list) > 0 else len(self.digit_list)

        #feedback_bar = FeedbackBar(0, self.bar_positions_list)
        alarmButtons = None
        feedbackBar = None
        rt_avarage = None
        if self.rt_practice != 0:
            rt_avarage = self.rt_practice;
        if self.use_bar:
            feedbackBar = FeedbackBar(0, rt_avarage, self.show_alarms)
        else:
            alarmButtons = AlarmButtons(self.screen_height, self.screen_width, self.rt_practice, self.show_alarms)

        grid = Grid(len(self.positions_list))

        pratice_trials = 0
        practice_correct = 0

        for trial in range(trials_number):
            target = None
            if len(self.digit_list) > 0:
                self.digit = self.digit_list[trial]
                audio = stimuli.Audio("./audio_final/" + str(self.digit) + ".wav")
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

            if self.use_bar:
                feedbackBar.paint_whole_line(canvas, self.last_trial_error, self.last_trial_rt, True)
            else:
                alarmButtons.paint_alarm_buttons(canvas, self.last_trial_error, self.last_trial_rt)
            canvas.present()
            if self.digit != None:
                audio.play()

            key, rt = self.exp.keyboard.wait([self.single_target, self.dual_target], stimuliDuration)
            if key is None:
                # we have waited stimuliDuration so we can remove
                #self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                if self.use_bar:
                    feedbackBar.paint_whole_line(canvas, False, None)
                else:
                    alarmButtons.paint_alarm_buttons(canvas, False, None)
                if self.use_bar:
                    self.play_aversive_sound_if_needed(feedbackBar)
                else:
                    self.play_aversive_sound_if_needed(alarmButtons)
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
                #self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                if self.use_bar:
                    feedbackBar.paint_whole_line(canvas, False, None)
                else:
                    alarmButtons.paint_alarm_buttons(canvas, False, None)
                if self.use_bar:
                    self.play_aversive_sound_if_needed(feedbackBar)
                else:
                    self.play_aversive_sound_if_needed(alarmButtons)
                grid.paint_grid(canvas)
                timeToClear = canvas.present()
                if target != None:
                    timeToUnload = target.unload()
                self.exp.clock.wait(ISI - timeToUnload - timeToClear)

            self.save_trial_data(key, rt, trial, alarmButtons)

        self.show_feedback_if_needed()
        #control.end(goodbye_text="T:hank you very much...", goodbye_delay=2000)

    def show_feedback_if_needed(self):
        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = str(int(self.correct_trials / self.trials_number * 100))
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))

            if self.is_dual_practice and self.hit_trials != 0:
                self.rt_practice = self.rt_practice / self.hit_trials

            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present();

    def save_trial_data(self, key, rt, counter, alarmButtons):
        alarm_played = alarmButtons.get_alarm_played();
        color = alarmButtons.get_color();
        time_from_start = datetime.datetime.now() - self.start_time
        if counter < self.n:
            self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, None, None, None,\
                               True, self.n, self.stress_condition, self.is_practice, color, alarm_played])
            self.correct_trials += 1
            self.last_trial_error = False
            self.last_trial_rt = None
            return

        if key == self.single_target:
            if self.digit != None and self.digit == self.digit_list[counter - self.n]:
                if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                    self.exp.data.add([str(datetime.datetime.now()),
                        self.digit, self.position_text, "Dual", self.single_target, rt, "Wrong Response",\
                                     False , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
                else:
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Auditory", self.single_target, rt,\
                                      "Correct Response", \
                                      True, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.correct_trials += 1
                    self.hit_trials += 1
                    if self.is_dual_practice == True:
                        self.rt_practice += rt
                    self.last_trial_error = False
                    self.last_trial_rt = rt
            elif self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, "Visual",\
                                   self.single_target, rt, "Correct Response", \
                                  True, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.correct_trials += 1
                self.hit_trials += 1
                if self.is_dual_practice == True:
                    self.rt_practice += rt
                self.last_trial_error = False
                self.last_trial_rt = rt
            else:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None,\
                                   self.single_target, rt, "FA", \
                                      False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

        elif key == self.dual_target:
            if self.digit != None and self.digit == self.digit_list[counter - self.n] and \
                self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "Dual",\
                     self.dual_target, rt, "Correct Response", \
                    True, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.correct_trials += 1
                self.hit_trials += 1
                if self.is_dual_practice == True:
                    self.rt_practice += rt
                self.last_trial_error = False
                self.last_trial_rt = rt
            elif self.digit != None and self.digit == self.digit_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   "Auditory", self.dual_target, rt, \
                                   "Wrong Response", False, self.n, self.stress_condition, self.is_practice,\
                                   color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

            elif self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "Visual", self.dual_target,\
                     rt, "Wrong Response", \
                        False , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None
            else:
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text,\
                     "None", self.dual_target, rt, "FA", \
                    False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

        else:
            if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                if self.digit != None and self.digit == self.digit_list[counter - self.n]:
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       "Dual", None, None, "MISS", \
                                       False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
                else:
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                       "Visual", None, None, "MISS", \
                                      False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
            elif self.digit != None and self.digit == self.digit_list[counter - self.n]:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   "Auditory", None, None, "MISS", \
                                  False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None
            else:
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   None, None, None, "Correct Rejection", \
                                 True , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = False
                self.last_trial_rt = None
                self.correct_trials += 1

    def play_aversive_sound_if_needed(self, alarm_class):
        should_play_alarm = alarm_class.should_play_alarm()
        if self.use_aversive_sound == False or should_play_alarm == False:
            return
        audio = None
        if should_play_alarm == True:
            audio = stimuli.Audio("./audio_final/Alarm_-12db.wav")

        #else:
            #num = random.randint(1,3)
            #if num == 2:
                #audio = stimuli.Audio("./audio_final/WhatsApp.wav")
        if audio != None:
            audio.preload()
            audio.play()
