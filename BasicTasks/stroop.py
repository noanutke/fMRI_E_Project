#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import stimuli, io
import datetime
import utils

class stroop:
    exp = None
    test_trials_number = 16
    practice_trials_number = 8
    test_up_key = 0
    test_down_key = 2

    practice_up_key = 1
    practice_down_key = 0

    up_key = -1
    down_key = -1
    possible_joystick_buttons = [0,1,2]
    up_direction = "pointing_up";
    down_direction = "pointing_down";

    def __init__(self, exp, lsl_stream, subNumber):
        self.subNumber = subNumber;
        self.order = ""
        self.outlet = lsl_stream
        self.correct_trials = 0
        self.exp = exp

        self.game_controller = io.GamePad(0, True, True)    #init joystick

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

    def run(self, block, is_practice, locations, directions, order, block_index=0):
        self.blockIndex = block_index
        self.correct_trials = 0
        self.order = order
        self.block = block
        self.is_practice = is_practice
        self.up_key = self.practice_up_key if self.is_practice else self.test_up_key
        self.down_key = self.practice_down_key if self.is_practice else self.test_down_key
        self.locations = locations
        self.directions = directions

        # send start stroop block LSL trigger
        utils.push_sample_current_time(self.outlet, ["startBlock_task_stroop_practice_" + ("1" if self.is_practice else "0") \
                                 + "_incong_" + ("1" if "incong" in self.block else "0") \
                                 + "_order_" + self.order \
                                 + "_subNumber_" + self.subNumber + "_blockIndex_" + str(block_index+1)])

        self.run_experiment()

        # send end stroop block LSL trigger
        utils.push_sample_current_time(self.outlet,["endBlock_task_stroop"])


    # run block
    def run_experiment(self):
        # define headers for expyriment log file output table (we currently don't use it,
        # but if we want - we can improve it and use it if we want
        self.exp.data_variable_names = ["time", "location", "direction", "trialType", "response", "rt"\
                                        ,"is success", "is practice", "blockType", "order"]

        currentTrailsNumber = self.test_trials_number;
        if self.is_practice:
            currentTrailsNumber = self.practice_trials_number;
        for trial_index in range(0, currentTrailsNumber):
            canvas = stimuli.BlankScreen()

            time_delay = 0

            # plot cross on canvas
            cross = stimuli.FixCross((50, 50), (0, 0), 5)
            time_delay += cross.plot(canvas)

            # plot arrow on canvas
            picture_arrow = stimuli.Picture(self.direction_file_converter[self.directions[trial_index]] \
                                            , position=self.locations_converter[self.locations[trial_index]])
            time_delay += picture_arrow.preload()
            time_delay += picture_arrow.plot(canvas)

            # show canvas
            time_delay += canvas.present();

            # send trigger to LSL with arrow details
            utils.push_sample_current_time(self.outlet, ["stimulus_task_stroop_type_arrow_location_" + ("u" if "up" in self.directions[trial_index] else "d") \
                                    + "_direction_"  + ("u" if "up" in self.locations[trial_index] else "d")])

            # wait for subject's response. Wait only for "duration" time
            key, rt = self.game_controller.wait_press(self.possible_joystick_buttons, self.duration,\
                                                      process_control_events=False)

            # we get here is subjects responded or of duration of stimulus ended
            if key != None: # subject responded and stimulus duration hasn't ended
                utils.push_sample_current_time(self.outlet, ["keyPressed_task_stroop_key_" + str(key)])
                self.exp.clock.wait(self.duration - rt) # wait the rest of the stimulus duration before going on

                # we get here when stimulus duration has ended (and subject responded)
                time_delay += self.paint_cross();
                self.exp.clock.wait(
                    self.isi - time_delay)  # wait for the ISI before going on

            else:
                # we get here if subject hasn't responded but stimulus duration ended - so we clean the screen
                time_delay += self.paint_cross();

                key = None;
                # we wait for subject to respond (but only for the ISI duration)
                key, rt = self.game_controller.wait_press(self.possible_joystick_buttons, self.isi - time_delay,
                                                          process_control_events=False)
                if key != None: # we get here if subject has responded - so we need to wait for the rest of
                                # the ISI
                    self.exp.clock.wait(
                        self.isi - rt - time_delay)  # wait the rest of the ISI before going on

                utils.push_sample_current_time(self.outlet, ["keyPressed_task_stroop_key_" + str(key)])
            self.save_trial_data(key, rt, trial_index)

        self.show_feedback_if_needed()

    def paint_cross(self):
        time_delay = 0
        canvas = stimuli.BlankScreen()
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        time_delay += cross.plot(canvas)
        time_delay += canvas.present()
        return time_delay;


    def is_success(self, direction, response_key):
        if response_key == self.up_key and direction == self.up_direction:
            self.correct_trials += 1
            return True
        elif response_key == self.down_key and direction == self.down_direction:
            self.correct_trials += 1
            return True
        else:
            return False

    def show_feedback_if_needed(self):
        currentTrialsNumber = self.test_trials_number;
        if self.is_practice:
            currentTrialsNumber = self.practice_trials_number;
        if self.is_practice == True:
            canvas = stimuli.BlankScreen()
            text_title = stimuli.TextLine("Success Rate", (0,0), text_size=(50))
            success_rate = str(float(self.correct_trials) / currentTrialsNumber * 100)
            text_number = stimuli.TextLine(success_rate + "%", position=(0, -100),\
                                           text_size=(50))

            text_title.plot(canvas)
            text_number.plot(canvas)
            canvas.present();

    def save_trial_data(self, key, rt, trial_index):
        is_success = self.is_success(self.directions[trial_index], key)
        utils.push_sample_current_time(self.outlet, \
                                       ["trialResult_task_stroop_success_" + ("1" if is_success else "0")])
        self.exp.data.add([str(datetime.datetime.now()),
                           self.locations[trial_index], self.directions[trial_index], \
                           key, rt, is_success, self.is_practice \
                              ,self.block, self.order])
