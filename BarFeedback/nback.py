#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar
from alarmButtons import AlarmButtons
from grid import Grid
import datetime
import pandas as pd
import time
import random
from pylsl import StreamInfo, StreamOutlet


class Nback:
    exp = None
    single_target = 0
    dual_target = 1
    n=0


    def __init__(self, develop_mode, start_time, screen_height, screen_width, start_fast, use_bar, outlet):
        self.trials_duration = []
        self.trials_duration_with_saving = []
        self.show_cross_for_seconds = 1;
        self.is_baseline = False
        self.outlet = outlet
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.start_time = start_time

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

    def run(self, n, stimuli_group, stimuli_type="both", block="", condition="", isBaseline=False):
        self.trials_number = 0
        self.correct_trials = 0
        self.hit_trials = 0
        self.digit_list = []
        self.positions_list = []
        self.positions_list_numbers = []
        self.colors_order_list = []
        self.alarms_order_list = []
        self.n = int(n)
        self.digit = None
        self.position = None
        self.position_text = None

        self.show_alarms = True if condition == "BlockProtocol_Stress" else False

        self.is_practice = True if stimuli_group == 'p' else False
        self.is_dual_practice = True if stimuli_group == 'p' and stimuli_type == 'both' else False
        self.is_baseline = isBaseline

        if self.is_practice == True:
            self.rt_practice = 0
            self.outlet.push_sample(["startBlock_practice"])
        if condition == "BlockProtocol_Stress":
            self.stress_condition = "sound"
            self.outlet.push_sample(["startBlock_stress_" + str(self.n)])
        else:
            self.stress_condition = "no"
            self.outlet.push_sample(["startBlock_noStress_" + str(self.n)])

        self.init_stimuli(n, stimuli_group, stimuli_type, block, condition)
        self.last_trial_error = False
        self.run_experiment()

    #digit_list = [1,1,1,2,5,3,5,5,7,8,9,10]

    def init_stimuli(self, n, stimuli_group, stimuli_type="both", block="", condition="", is_baseline=True):
        # Assign spreadsheet filename to `file`
        file = './' + condition + '.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse(block)

        number = 0
        for values in df1.values:
            if number >= 12:
               break
            if stimuli_type == 'a' or stimuli_type == "both":
                self.digit_list.insert(len(self.digit_list), values[0])
            if stimuli_type == 'v' or stimuli_type == "both":
                self.positions_list_numbers.insert(len(self.positions_list), values[1])
                self.positions_list.insert(len(self.positions_list), Grid.positions_indices[int(values[1])-1])
            if condition == "BlockProtocol_Stress":
                self.colors_order_list.insert(len(self.digit_list), values[2])
                self.alarms_order_list.insert(len(self.digit_list), values[3])

            self.trials_number += 1
            number += 1


    def paint_cross(self, exp):
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        canvas = stimuli.BlankScreen()
        cross.plot(canvas)
        canvas.present()
        exp.clock.wait(self.show_cross_for_seconds * 1000)

    def run_experiment(self):
        game1 = io.GamePad(0, True, True)
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
            alarmButtons = AlarmButtons(self.screen_height, self.screen_width, self.colors_order_list,\
                                    self.alarms_order_list, self.outlet, self.show_alarms)

        grid = Grid(len(self.positions_list))

        pratice_trials = 0
        practice_correct = 0

        self.paint_cross(self.exp)
        start_all = time.time()
        for trial in range(trials_number):
            start = time.time()

            target = None
            if len(self.digit_list) > 0:
                self.digit = self.digit_list[trial]
                audio = stimuli.Audio("./audio_final/" + str(int(self.digit)) + ".wav")
                audio.preload()
            canvas = stimuli.BlankScreen()
            #target = stimuli.TextLine(text=str(digit), text_size=80)
            time_delay_for_isi = 0
            if len(self.positions_list) > 0:
                self.position_text = self.positions_list[trial]
                self.position = Grid.positions_locations[self.position_text]
                target = stimuli.Rectangle((30,30), misc.constants.C_BLACK, 0, None, None, self.position)

                time_delay_for_isi += target.preload()
                time_delay_for_isi += target.plot(canvas)
                time_delay_for_isi += grid.paint_grid(canvas)

            if self.use_bar:
                feedbackBar.paint_whole_line(canvas, self.last_trial_error, self.last_trial_rt, True)
            else:
                time_delay_for_isi += alarmButtons.paint_alarm_buttons(canvas)

            time_delay_for_isi += canvas.present()

            if self.digit != None:
                audio.play()
                self.outlet.push_sample(["audioStim_" + str(self.digit)])
                audio.unload()



            if len(self.positions_list) > 0:
                self.outlet.push_sample(["visualStim_" + self.position_text])

            key, rt = game1.wait_press([self.single_target, self.dual_target], stimuliDuration, process_control_events=False)
            if key is None:
                # we have waited stimuliDuration so we can remove
                #self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()
                time_delay_after_stimuli = 0
                if self.use_bar:
                    time_delay_after_stimuli += feedbackBar.paint_whole_line(canvas, False, None)
                    self.play_aversive_sound_if_needed(feedbackBar)
                else:
                    time_delay_after_stimuli += alarmButtons.paint_alarm_buttons(canvas, False)
                    self.play_aversive_sound_if_needed(alarmButtons)

                time_delay_after_stimuli += grid.paint_grid(canvas)
                time_delay_after_stimuli += canvas.present()
                if target != None:
                    time_delay_after_stimuli += target.unload()
                key, rt = game1.wait_press([self.single_target, self.dual_target], ISI\
                                                 - time_delay_after_stimuli- time_delay_for_isi)
                if key != None:
                    self.outlet.push_sample(["response_" + str(key)])
                    self.exp.clock.wait(ISI - rt - time_delay_for_isi - time_delay_after_stimuli) # wait the rest of the ISI before going on
                    rt = rt + stimuliDuration + time_delay_after_stimuli
            else:
                self.outlet.push_sample(["response_" + str(key)])
                self.exp.clock.wait(stimuliDuration - rt) # wait the rest of the stimuliDuration before removing
                # we have now waited stimuliDuration so we can remove
                #self.play_aversive_sound_if_needed(feedback_bar)
                canvas = stimuli.BlankScreen()

                if self.use_bar:
                    time_delay_for_isi += feedbackBar.paint_whole_line(canvas, False, None)
                else:
                    time_delay_for_isi += alarmButtons.paint_alarm_buttons(canvas, False)
                if self.use_bar:
                    self.play_aversive_sound_if_needed(feedbackBar)
                else:
                    self.play_aversive_sound_if_needed(alarmButtons)
                time_delay_for_isi += grid.paint_grid(canvas)
                time_delay_for_isi += canvas.present()
                if target != None:
                    time_delay_for_isi += target.unload()
                self.exp.clock.wait(ISI - time_delay_for_isi)

            end = time.time()
            self.trials_duration.insert(len(self.trials_duration), end-start)
            self.save_trial_data(key, rt, trial, alarmButtons)
            end = time.time()
            self.trials_duration_with_saving.insert(len(self.trials_duration_with_saving), end - start)

        end_all = time.time()
        #print (end_all-start_all)
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
        alarm_played = False;
        color = "green"
        if self.show_alarms == True:
            alarm_played = self.alarms_order_list[counter] == "alarm"
            color = self.colors_order_list[counter]

        time_from_start = datetime.datetime.now() - self.start_time

        response_to_target = ""
        if self.is_baseline:
            position_number = self.positions_list_numbers[counter]
            response = ""
            if key == self.single_target:
                if (self.digit == self.n and position_number != self.n) or (self.digit != self.n and position_number == self.n):
                    target = "Auditory"
                    if position_number == self.n:
                        target = "Visual"
                    response_to_target= "Correct Response_" + target
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, target,\
                                       self.single_target, rt,\
                                      "Correct Response", \
                                      True, self.n, "baseline", self.is_practice, color, alarm_played])
                elif position_number == self.n and self.digit == self.n:
                    response_to_target = "Wrong Response_dual"
                    self.exp.data.add([str(datetime.datetime.now()),
                        self.digit, self.position_text, "Dual", self.single_target, rt, "Wrong Response",\
                                     False , self.n, "baseline", self.is_practice, color, alarm_played])
                else:
                    response_to_target_ = "FA_none"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, \
                                       self.single_target, rt, "FA", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
            elif key == self.dual_target:
                if position_number == self.n and self.digit == self.n:
                    response_to_target = "Correct Response_dual"
                    self.exp.data.add(
                        [str(datetime.datetime.now()), self.digit, self.position_text, "Dual", \
                         self.dual_target, rt, "Correct Response", \
                         True, self.n, "baseline", self.is_practice, color, alarm_played])
                elif position_number == self.n:
                    response_to_target = "Wrong Response_visual"
                    self.exp.data.add([str(datetime.datetime.now()),
                        self.digit, self.position_text, "Visual", self.single_target, rt, "Wrong Response",\
                                     False , self.n, "baseline", self.is_practice, color, alarm_played])
                elif self.digit == self.n:
                    response_to_target = "Wrong Response_auditory"
                    self.exp.data.add([str(datetime.datetime.now()),
                                       self.digit, self.position_text, "Auditory", self.single_target, rt,
                                       "Wrong Response", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
                else:
                    response_to_target = "FA_none"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, \
                                       self.single_target, rt, "FA", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
            else:
                response_to_target = "MISS_dual"
                if position_number == self.n and self.digit == self.n:
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       "Dual", None, None, "MISS", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
                elif position_number == self.n :
                    response_to_target = "MISS_visual"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       "Visual", None, None, "MISS", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
                elif self.digit == self.n:
                    response_to_target = "MISS_auditory"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       "Auditory", None, None, "MISS", \
                                       False, self.n, "baseline", self.is_practice, color, alarm_played])
                else:
                    response_to_target= "Correct Rejection"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       None, None, None, "Correct Rejection", \
                                       True, self.n, "baseline", self.is_practice, color, alarm_played])


        if counter < self.n:
            response_to_target = "First_trials"
            self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None, None, None, None,\
                               True, self.n, self.stress_condition, self.is_practice, color, alarm_played])
            self.correct_trials += 1
            self.last_trial_error = False
            self.last_trial_rt = None
            return

        if key == self.single_target:
            response_to_target_ = "First_trials"
            if self.digit != None and self.digit == self.digit_list[counter - self.n]:

                if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                    response_to_target = "Wrong Response_dual"
                    self.exp.data.add([str(datetime.datetime.now()),
                        self.digit, self.position_text, "Dual", self.single_target, rt, "Wrong Response",\
                                     False , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
                else:
                    response_to_target = "Correct Response_auditory"
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
                response_to_target = "Correct Response_visual"
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
                response_to_target = "FA"
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, None,\
                                   self.single_target, rt, "FA", \
                                      False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

        elif key == self.dual_target:
            if self.digit != None and self.digit == self.digit_list[counter - self.n] and \
                self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                response_to_target = "Correct Response_dual"
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
                response_to_target = "Wrong Response_auditory"
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   "Auditory", self.dual_target, rt, \
                                   "Wrong Response", False, self.n, self.stress_condition, self.is_practice,\
                                   color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

            elif self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                response_to_target = "Wrong Response_visual"
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text, "Visual", self.dual_target,\
                     rt, "Wrong Response", \
                        False , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None
            else:
                response_to_target = "FA"
                self.exp.data.add(
                    [str(datetime.datetime.now()), self.digit, self.position_text,\
                     "None", self.dual_target, rt, "FA", \
                    False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None

        else:
            if self.position_text != None and self.position_text == self.positions_list[counter - self.n]:
                if self.digit != None and self.digit == self.digit_list[counter - self.n]:
                    response_to_target = "MISS_dual"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, \
                                       "Dual", None, None, "MISS", \
                                       False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
                else:
                    response_to_target = "MISS_visual"
                    self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                       "Visual", None, None, "MISS", \
                                      False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                    self.last_trial_error = True
                    self.last_trial_rt = None
            elif self.digit != None and self.digit == self.digit_list[counter - self.n]:
                response_to_target = "MISS_auditory"
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   "Auditory", None, None, "MISS", \
                                  False, self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = True
                self.last_trial_rt = None
            else:
                response_to_target = "Correct Rejection"
                self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text,\
                                   None, None, None, "Correct Rejection", \
                                 True , self.n, self.stress_condition, self.is_practice, color, alarm_played])
                self.last_trial_error = False
                self.last_trial_rt = None
                self.correct_trials += 1

        self.outlet.push_sample([response_to_target])

    def play_aversive_sound_if_needed(self, alarm_class):
        should_play_alarm = alarm_class.should_play_alarm()
        if self.show_alarms == False or should_play_alarm == False:
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
            self.outlet.push_sample(["alarm"])
