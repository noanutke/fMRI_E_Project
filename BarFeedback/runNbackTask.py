from __future__ import division
from nback import Nback
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime
import random
from pylsl import StreamInfo, StreamOutlet
import pandas as pd
import pygame
from psychopy import parallel

class runNbackTask:
    instructions_folder = "instructions_pilot_mode_new"
    use_pilot_mode = True
    use_develop_mode = True
    flight_simulator_mode = True



    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width):
        self.baseline_targets = [4,5]
        random.shuffle(self.baseline_targets)
        self.is_baseline = False
        self.blocks_order = []
        self.letters_lists = []
        self.locations_lists = []
        info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'myuidw43536')
        self.outlet = StreamOutlet(info)
        self.start_time = datetime.datetime.now()
        self.experiment = Nback(self.use_develop_mode, self.start_time, screen_height, screen_width, True, False, \
                                self.outlet)
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        self.stress_evaluation_log = WriteToExcel("stress_evaluation_" + current_hour + "_" + current_min, "stress")
        self.cognitive_load_log = WriteToExcel("cognitive_load_evaluation_" + current_hour + "_" + current_min, "load")
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.condition = self.choose_condition()

        if self.condition != "BlockProtocol_Practice":
            self.choose_blocks_order()
            self.init_trials_lists()
        else:
            self.blocks_order = ["Sheet1", "Sheet1", "Sheet1"]

        self.run_blocks();
        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()

    def init_trials_lists(self):
        baseline_index = 0
        baseline_target = -1
        for i in range(len(self.blocks_order)):
            if self.blocks_order[i] == 0:
                baseline_target = self.baseline_targets[baseline_index]
                baseline_index += 1

            rand = random.randint(1,2)
            letters_targets_amount = 0
            locations_targets_amount = 0
            if rand == 1:
                letters_targets_amount = 2
                locations_targets_amount = 3
            else:
                letters_targets_amount = 3
                locations_targets_amount = 2

            letters_lists, location_target_index = self.generate_trials\
                (self.blocks_order[i], letters_targets_amount, baseline_target, -1)
            locations_lists, index = self.generate_trials\
                (self.blocks_order[i], locations_targets_amount, baseline_target, location_target_index)

            self.letters_lists.insert(i, letters_lists)
            self.locations_lists.insert(i, locations_lists)



    def choose_blocks_order(self):
        blocks1 = [0,1,2,3]
        blocks2 = [0,1,2,3]
        random.shuffle(blocks1)
        random.shuffle(blocks2)
        blocks1.extend(blocks2)
        self.blocks_order = blocks1


    def choose_condition(self):
        condition = self.ask_for_condition()
        if condition == "practice":
            return "BlockProtocol_Practice"
        elif condition == "stress":
            return "BlockProtocol_Stress"
        else:
            return "BlockProtocol_NoStress"

    def check_if_target_demands_ok(self, indices):
        target_in_row = 1
        i = 0
        for index in indices:
            if i == 0:
                i += 1
                continue
            if index == indices[i-1] + 1:
                target_in_row += 1
                if target_in_row >= 3:
                    return False
            else:
                target_in_row = 1
        return True

    def check_if_trials_order_ok(self, trials):
        same_in_row = 1
        i = 0
        for trial in trials:
            if i == 0:
                i += 1
                continue
            if trial == trials[i-1]:
                same_in_row += 1
                if same_in_row >= 4:
                    return False
            else:
                same_in_row = 1
        return True

    def generate_trials(self, n, targets_amount, baseline_target, dual_target_index):

        trials_amount = 12
        target_demands_ok = False
        while target_demands_ok == False:
            target_indices = []
            targets_amount_corrected = targets_amount
            if dual_target_index > -1:
                target_indices.insert(0, dual_target_index)
                targets_amount_corrected -= 1


            for i in range(targets_amount_corrected):
                index = random.randint(n,11)
                if index in target_indices:
                    continue
                target_indices.insert(0, index)
            if self.check_if_target_demands_ok(target_indices):
                target_demands_ok = True


        target_indices.sort()
        trials_order_ok = False
        while trials_order_ok == False:
            trials = []
            target_index = 0
            for i in range(trials_amount):

                if target_index < len(target_indices) and target_indices[target_index] == i:
                    target_index += 1
                    if n == 0:
                        trials.insert(i, baseline_target)
                    else:
                        trials.insert(i, trials[i-n])

                else:
                    trial = random.randint(1,7)
                    value_to_exclude = baseline_target
                    if n != 0 and i-n >= 0:
                        value_to_exclude = trials[i-n]
                    if trial >= value_to_exclude:
                        trial += 1

                    trials.insert(i, trial)

                if self.check_if_trials_order_ok(trials):
                    trials_order_ok = True

        dual_target_index = target_indices[random.randint(0, len(target_indices)-1)]
        return (trials, dual_target_index)



    def ask_for_condition(self):
        canvas = stimuli.BlankScreen()
        Practice = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_Practice = stimuli.TextLine(text="Practice", position=Practice.position,
                                 text_colour=misc.constants.C_WHITE)
        Basic = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_Basic = stimuli.TextLine(text="Basic", position=Basic.position,
                                 text_colour=misc.constants.C_WHITE)

        Manipulation = stimuli.Rectangle(size=(100, 80), position=(0, 0))
        text_Manipulation = stimuli.TextLine(text="Manipulation", position=Manipulation.position,
                                 text_colour=misc.constants.C_WHITE)


        Practice.plot(canvas)
        text_Practice.plot(canvas)

        Basic.plot(canvas)
        text_Basic.plot(canvas)

        Manipulation.plot(canvas)
        text_Manipulation.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if Practice.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'practice'
            elif Basic.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'noStress'
            elif Manipulation.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'stress'

    def run_blocks(self):
        evaluate_stress_first_time = False
        practice_block = 0
        block_index = 0
        for block in self.blocks_order:
            n = block
            self.is_baseline = False
            if n == 0:
                self.is_baseline = True
                target = self.baseline_targets[0]
                n = target
                self.baseline_targets.pop(0)

            stay_on_block = True
            stimuli_type = "both"

            block_type = ""
            if self.condition == "BlockProtocol_Practice":
                n = 1
                block_type = 'p'
                if practice_block == 0:
                    stimuli_type = 'v'
                elif practice_block == 1:
                    stimuli_type = 'a'
                else:
                    stimuli_type = 'both'
                practice_block += 1

            while stay_on_block:

                if block_type != 'p' and evaluate_stress_first_time == False:
                    self.evaluate_stress(str(block))
                    evaluate_stress_first_time = True

                if self.is_baseline == True: #baseline
                    rest = RestBlock(self.outlet, str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     "", "./pictures/"+\
                                     self.instructions_folder + "/Slide" + str(n) + "_baseline.png")
                else:
                    rest = RestBlock(self.outlet, str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     self.instructions_folder)

                port = parallel.ParallelPort(address='0xE010')
                port.setData(1)
                n_back = self.experiment.run(n, self.letters_lists[block_index], self.locations_lists[block_index],\
                                             block_type, stimuli_type, block, self.condition, self.is_baseline)
                port.setData(2)
                block_index += 1
                if block_type == 'p':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    stay_on_block = False
                    self.evaluate_stress(str(block) + "_" + self.condition)
                    self.evaluate_load(str(block) + "_" + self.condition)



    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block, self.outlet)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block, self.outlet)