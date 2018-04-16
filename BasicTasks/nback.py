#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import stimuli, misc, io
from grid import Grid
import datetime
import utils

class Nback:
    exp = None
    test_single_target = 2
    test_dual_target = 0

    practice_single_target = 0
    practice_dual_target = 1

    single_target = -1
    dual_target = -1

    n=0
    targets_amount = 4;
    possible_joystick_buttons = [0,1,2]

    ISI = 2500
    stimuli_duration = 500
    sounds_folder = "./audio_final/"
    sound_files_suffix = ".wav"


    def __init__(self, exp, outlet, subNumber):

        self.subNumber = subNumber
        self.show_cross_for_seconds = 1;
        self.is_baseline = False
        self.outlet = outlet

        self.exp = exp
        self.digit = None
        self.position = None
        self.is_practice = False
        self.is_dual_practice = False   # true if the current block is practice with both modailities
        self.correct_trials = 0
        self.hit_trials = 0
        self.FA_trials = 0
        self.rt_practice = 0
        self.trials_number = 0
        self.last_trial_error = False
        self.last_trial_rt = None
        self.order = ""
        self.stimuli_type = ""
        self.blockIndex = 0

    def run(self, n, letters_list, locations_list, is_practice, stimuli_type="both",\
            isBaseline=False, order = "", block_index=0):
        self.blockIndex = block_index;
        self.stimuli_type = stimuli_type
        self.with_audio_stimuli = False if stimuli_type == "v" else True
        self.with_visual_stimuli = False if stimuli_type == "a" else True
        self.correct_trials = 0
        self.order = order
        self.trials_number = 0
        self.correct_trials = 0
        self.hit_trials = 0
        self.digit_list = []
        self.positions_list_text = []
        self.positions_list_numbers = []

        self.n = int(n)
        self.digit = None
        self.position = None
        self.position_text = None

        self.is_practice = is_practice
        self.is_dual_practice = True if is_practice and stimuli_type == 'both' else False
        self.single_target = self.practice_single_target if self.is_practice else self.test_single_target
        self.dual_target = self.practice_dual_target if self.is_practice else self.test_dual_target

        self.is_baseline = isBaseline

        # send start nBack block LSL trigger
        utils.push_sample_current_time(self.outlet, ["startBlock_task_nBack_practice_" + ("1" if self.is_practice else "0") \
                                 + "_baseline_" + ("1" if self.is_baseline else "0") \
                                 + "_level_" + str(self.n) + "_order_" + self.order \
                                 + "_subNumber_" + self.subNumber + "_blockIndex_" + str(block_index+1)])

        self.init_stimuli(letters_list, locations_list)

        self.last_trial_error = False
        self.run_experiment()

        # send end nBack block LSL trigger
        utils.push_sample_current_time(self.outlet, ["endBlock_task_nBack"] )


    def init_stimuli(self, letters_list, locations_list):
        if self.with_audio_stimuli:
            for letter in letters_list:
                self.digit_list.insert(len(self.digit_list), str(letter))

        if self.with_visual_stimuli:
            for location in locations_list:
                self.positions_list_numbers.insert(len(self.positions_list_numbers),str(location))
                self.positions_list_text.insert(len(self.positions_list_text), Grid.positions_indices[location - 1])


    def paint_cross(self, exp):
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        canvas = stimuli.BlankScreen()
        cross.plot(canvas)
        canvas.present()
        exp.clock.wait(self.show_cross_for_seconds * 1000)

    def run_experiment(self):
        game1 = io.GamePad(0, True, True)   #init joystick

        # define headers for expyriment log file output table (we currently don't use it,
        # but if we want - we can improve it and use it if we want
        self.exp.data_variable_names = ["time", "digit", "position", "targetType", "response", "rt",\
                                        "responseType", "is success", "n", "order", "is practice"]

        self.trials_number = len(self.positions_list_text) if len(self.positions_list_text) > 0 else len(self.digit_list)

        # create grid
        grid = Grid(len(self.positions_list_text))\


        for trial in range(self.trials_number):
            target = None
            if self.with_audio_stimuli:  # we have auditory stimuli in this block
                # so we initialize the auditory stimulus
                self.digit = self.digit_list[trial]
                audio = stimuli.Audio(self.sounds_folder + str(int(self.digit)) + self.sound_files_suffix)
                audio.preload()

            canvas = stimuli.BlankScreen()
            time_delay_for_isi = 0
            if self.with_visual_stimuli: # we have visual stimuli in this block
                # so we initialize the visual stimuus
                self.position_text = self.positions_list_text[trial]
                self.position = Grid.positions_locations[self.position_text]
                target = stimuli.Rectangle((30,30), misc.constants.C_BLACK, 0, None, None, self.position)
                time_delay_for_isi += target.preload()
                time_delay_for_isi += target.plot(canvas)

            #prepare grid on canvas
            time_delay_for_isi += grid.paint_grid(canvas)
            #show canvas
            time_delay_for_isi += canvas.present()

            if self.with_audio_stimuli:
                audio.play()    # we have auditory stimuli so we play the letter now
                utils.push_sample_current_time(self.outlet,\
                                               ["stimulus_task_nBack_type_letter_letter_" + str(self.digit)])
                audio.unload()

            if self.with_visual_stimuli:
                utils.push_sample_current_time(self.outlet, \
                                               ["stimulus_task_nBack_type_vis_location_" + self.position_text])


            # wait for subject's response. Wait only for "duration" time
            key, rt = game1.wait_press(self.possible_joystick_buttons, self.stimuli_duration, process_control_events=False)
            if key is None:
                # we have now waited stimuliDuration so we can remove stimulus
                canvas = stimuli.BlankScreen()
                time_delay_for_isi += grid.paint_grid(canvas)
                time_delay_for_isi += canvas.present()

                time_delay_after_stimuli = 0

                time_delay_after_stimuli += grid.paint_grid(canvas)


                time_delay_after_stimuli += canvas.present()
                if target != None:
                    time_delay_after_stimuli += target.unload()

                # we wait for subject to respond (but only for the ISI duration)
                key, rt = game1.wait_press(self.possible_joystick_buttons, self.ISI\
                                                 - time_delay_after_stimuli- time_delay_for_isi)
                if key != None:# we get here if subject has responded - so we need to wait for the rest of
                                # the ISI
                    utils.push_sample_current_time(self.outlet, ["keyPressed_task_nBack_key_" + str(key)] )

                    # wait the rest of the ISI before going on
                    self.exp.clock.wait(self.ISI - rt - time_delay_for_isi - time_delay_after_stimuli) # wait the rest of the ISI before going on
                    rt = rt + self.stimuli_duration + time_delay_after_stimuli
            else:   # subject responded and stimulus duration hasn't ended
                utils.push_sample_current_time(self.outlet, ["keyPressed_task_nBack_key_" + str(key)])

                # wait the rest of the stimulus duration before going on
                self.exp.clock.wait(self.stimuli_duration - rt) # wait the rest of the stimuliDuration before removing
                # we have now waited stimuliDuration so we can remove stimulus
                canvas = stimuli.BlankScreen()
                time_delay_for_isi += grid.paint_grid(canvas)
                time_delay_for_isi += canvas.present()
                if target != None:
                    time_delay_for_isi += target.unload()

                # wait for the ISI before going on
                self.exp.clock.wait(self.ISI - time_delay_for_isi)

            self.save_trial_data(key, rt, trial)

        self.show_feedback_if_needed()

    def show_feedback_if_needed(self):
        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = int(float(self.hit_trials) / self.targets_amount * 100) - \
                               int(float(self.FA_trials) / (self.trials_number - self.targets_amount) * 100)
            if success_rate < 0:
                success_rate = "0";
            if success_rate > 100:
                success_rate = "100";
            else:
                success_rate = str(success_rate)
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))
            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present();

    def get_target_type(self, counter):

        is_auditory_target = False;
        is_visual_target = False
        if self.with_audio_stimuli:
            if (self.is_baseline and int(self.digit) == self.n) or \
                 not self.is_baseline and \
                 counter >= self.n and self.digit == self.digit_list[counter - self.n]:
                 is_auditory_target = True
        if self.with_visual_stimuli:
            position_number = int(self.positions_list_numbers[counter])
            if (self.is_baseline and position_number == self.n) or \
                 (not self.is_baseline and \
                 counter >= self.n and position_number == int(self.positions_list_numbers[counter - self.n])):
                 is_visual_target = True

        if is_visual_target and is_auditory_target:
            return "Dual"
        elif is_visual_target:
            return "Visual"
        elif is_auditory_target:
            return "Auditory"
        else:
            return None

    def get_response_to_target(self, target, key):
        correct_response_prefix = "CorrectResponse"
        FA_prefix = "FA"
        MISS_prefix = "MISS"
        wrong_response_prefix = "WrongResponse"
        correct_rejection = "CorrectRejection"

        if key == self.dual_target:
            if target == "Dual":
                self.hit_trials += 1;
                return (correct_response_prefix + target, True)
            elif target is None:
                self.FA_trials += 1;
                return (FA_prefix, False)
            else:
                return (wrong_response_prefix + target, False)
        elif key == self.single_target:
            if target == "Auditory" or target == "Visual" :
                self.hit_trials += 1;
                return (correct_response_prefix + target, True)
            elif target is None:
                self.FA_trials += 1;
                return (FA_prefix, False)
            else:
                return (wrong_response_prefix + target, False)
        else:
            if target is None:
                return (correct_rejection, True)
            else:
                return (MISS_prefix + target, False)


    def save_trial_data(self, key, rt, counter):
        target_type = self.get_target_type(counter)
        response_to_target, is_success = self.get_response_to_target(target_type,key)

        self.exp.data.add([str(datetime.datetime.now()), self.digit, self.position_text, target_type, \
                           key, rt, response_to_target, is_success, self.n, self.order, self.is_practice])

        utils.push_sample_current_time(self.outlet, ["trialResultDescription_task_nBack_resultType_" + response_to_target])

        expected_response = "1";
        actual_response = "1";

        if target_type == "Dual":
            expected_response = "2"
        elif target_type is None:
            expected_response = "0"

        if key == self.dual_target:
            actual_response = "2"
        elif key is None:
            actual_response = "0"
        utils.push_sample_current_time(self.outlet, ["trialResult_task_nBack_expected_" + expected_response + \
                                 "_actual_" + actual_response])

