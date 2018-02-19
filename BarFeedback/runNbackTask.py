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

    flight_simulator_mode = True



    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width, exp, use_develop_mode):
        self.use_develop_mode = use_develop_mode
        self.exp = exp
        self.fixationTimes = [6,6,9,9,9,3,3,3]
        random.shuffle(self.fixationTimes)
        self.baseline_targets = [4,5]
        random.shuffle(self.baseline_targets)
        self.is_baseline = False
        self.current_block_order_number = ""
        self.blocks_order = []
        self.letters_lists = []
        self.locations_lists = []
        info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'myuidw43536')
        self.outlet = StreamOutlet(info)
        self.start_time = datetime.datetime.now()
        self.experiment = Nback(self.exp, self.start_time, screen_height, screen_width, True, False, \
                                self.outlet)
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        self.stress_evaluation_log = WriteToExcel("stress_evaluation_" + current_hour + "_" + current_min, "stress")
        self.cognitive_load_log = WriteToExcel("cognitive_load_evaluation_" + current_hour + "_" + current_min, "load")
        self.screen_height = screen_height
        self.screen_width = screen_width


        self.start_again = True
        while self.start_again == True:
            self.start_again = False
            self.condition = self.choose_condition()
            if self.condition != "BlockProtocol_Practice":
                self.ask_for_order()
                #self.choose_blocks_order(self.current_block_order_number)

                #self.init_trials_lists(True, self.current_block_order_number)


                self.init_blocks_order_from_file()
                self.init_stimuli_from_file()

            else:
                level = self.ask_for_level()
                self.blocks_order = [level + "_a"]
                self.init_trials_lists(False, "")


            self.run_blocks();
            self.stress_evaluation_log.close_file()
            self.cognitive_load_log.close_file()


    def init_blocks_order_from_file(self):
        # Load spreadsheet
        xl = pd.read_csv("./orders/order" + self.current_block_order_number + ".csv")
        #df1 = xl.parse("Sheet1")

        for values in xl:
            self.blocks_order.insert(len(self.blocks_order), values)

    def init_trials_lists(self, init_from_file, order=""):
        baseline_index = 0
        baseline_target = -1

        for i in range(len(self.blocks_order)):
            nLevel = int(self.blocks_order[i].split('_')[0])
            type = self.blocks_order[i].split('_')[1]

            if nLevel == 0:
                if type == "a":
                    baseline_target = 4
                else:
                    baseline_target= 5

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
                (nLevel, letters_targets_amount, baseline_target, -1)
            locations_lists, index = self.generate_trials\
                (nLevel, locations_targets_amount, baseline_target, location_target_index)

            if init_from_file != True:
                self.letters_lists.insert(i, letters_lists)
                self.locations_lists.insert(i, locations_lists)
            else:
                type = "a"
                if i > 3:
                    type = "b"
                excel_writer = WriteToExcel("./orders/order" + order + "_" + str(self.blocks_order[i]), None)
                excel_writer.add_row(letters_lists)
                excel_writer.add_row(locations_lists)
                excel_writer.close_file()


    def init_stimuli_from_file(self):

        index = 0
        for block in self.blocks_order:

            # Load spreadsheet
            xl = pd.read_csv("./orders/order" + self.current_block_order_number + "_" + block + ".csv", header=None)
            letters = []
            locations = []

            for value in range(0,12):
                letters.insert(len(letters), xl[value][0])
                locations.insert(len(letters), xl[value][1])

            self.letters_lists.insert(index, letters)
            self.locations_lists.insert(index, locations)
            index += 1;


    def choose_blocks_order(self, order):
        blocks1 = ["0_a","1_a","2_a","3_a"]
        blocks2 = ["0_b","1_b","2_b","3_b"]
        random.shuffle(blocks1)
        random.shuffle(blocks2)
        blocks1.extend(blocks2)
        self.blocks_order = blocks1
        excel_writer = WriteToExcel("./orders/order" + order, None)
        excel_writer.add_row(blocks1)
        excel_writer.close_file()


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

    def ask_for_order(self):
        canvas = stimuli.BlankScreen()
        order1_ = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        Order1 = stimuli.TextLine(text="Order1", position=order1_.position,
                                 text_colour=misc.constants.C_WHITE)
        order2_ = stimuli.Rectangle(size=(100, 80), position=(-70, 0))
        Order2 = stimuli.TextLine(text="Order2", position=order2_.position,
                                 text_colour=misc.constants.C_WHITE)

        order3_ = stimuli.Rectangle(size=(100, 80), position=(60, 0))
        Order3 = stimuli.TextLine(text="Order3", position=order3_.position,
                                 text_colour=misc.constants.C_WHITE)

        order4_ = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        Order4 = stimuli.TextLine(text="Order4", position=order4_.position,
                                 text_colour=misc.constants.C_WHITE)


        order1_.plot(canvas)
        Order1.plot(canvas)

        order2_.plot(canvas)
        Order2.plot(canvas)

        order3_.plot(canvas)
        Order3.plot(canvas)

        order4_.plot(canvas)
        Order4.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if order1_.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.current_block_order_number = '1'
                return

            elif order2_.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.current_block_order_number = '2'
                return

            elif order3_.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.current_block_order_number = '3'
                return

            elif order4_.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.current_block_order_number = '4'
                return

    def ask_for_level(self):
        canvas = stimuli.BlankScreen()
        level1 = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_level1 = stimuli.TextLine(text="1 back", position=level1.position,
                                 text_colour=misc.constants.C_WHITE)
        level2 = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_level2 = stimuli.TextLine(text="2 back", position=level2.position,
                                 text_colour=misc.constants.C_WHITE)

        level3 = stimuli.Rectangle(size=(100, 80), position=(0, 0))
        text_level3 = stimuli.TextLine(text="3 back", position=level3.position,
                                 text_colour=misc.constants.C_WHITE)


        level1.plot(canvas)
        text_level1.plot(canvas)

        level2.plot(canvas)
        text_level2.plot(canvas)

        level3.plot(canvas)
        text_level3.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if level1.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "1"
            elif level2.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "2"
            elif level3.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "3"


    def ask_for_condition(self):
        canvas = stimuli.BlankScreen()
        Practice = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_Practice = stimuli.TextLine(text="Practice", position=Practice.position,
                                 text_colour=misc.constants.C_WHITE)
        Basic = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_Basic = stimuli.TextLine(text="Test", position=Basic.position,
                                 text_colour=misc.constants.C_WHITE)


        Practice.plot(canvas)
        text_Practice.plot(canvas)

        Basic.plot(canvas)
        text_Basic.plot(canvas)

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

    def run_blocks(self):
        evaluate_stress_first_time = False
        practice_block = 0
        block_index = 0
        for block in self.blocks_order:
            n = int(block.split('_')[0])
            type = block.split('_')[1]
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
                self.start_again = True
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
                    rest = RestBlock(self.outlet, self.fixationTimes[block_index],\
                                     str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     "", "./pictures/"+\
                                     self.instructions_folder + "/Slide" + str(n) + "_baseline.png")
                else:
                    rest = RestBlock(self.outlet, self.fixationTimes[block_index],\
                                     str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     self.instructions_folder)

                port = parallel.ParallelPort(address='0xE010')
                port.setData(int(1))
                n_back = self.experiment.run(n, self.letters_lists[block_index], self.locations_lists[block_index],\
                                             block_type, stimuli_type, block, self.condition, self.is_baseline)
                port.setData(int(2))

                if block_type == 'p':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        block_index += 1
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    block_index += 1
                    stay_on_block = False
                    if block_index == 4 or block_index == 8:
                        self.evaluate_stress(str(block) + "_" + self.condition)
                        self.evaluate_load(str(block) + "_" + self.condition)



    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block, self.outlet)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block, self.outlet)