from __future__ import division
from stroop import stroop
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime
import random
from random import shuffle
from pylsl import StreamInfo, StreamOutlet
import pandas as pd
import numpy
from psychopy import parallel

class runStroopTask:
    use_pilot_mode = True
    use_develop_mode = False
    flight_simulator_mode = True

    folder = './NewStroop'
    instructions_folder = 'pictures/instructions_stroop'
    instructions_file = 'instructions.png'

    allBlocks = ['high', 'low', 'medium', 'baseline','high', 'low', 'medium', 'baseline',\
                 'high', 'low', 'medium', 'baseline']

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width):
        self.blocks_order = []
        self.trials_locations_array = []
        self.trials_directions_array = []
        shuffle(self.allBlocks)
        info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'myuidw43536')
        self.outlet = StreamOutlet(info)
        self.start_time = datetime.datetime.now()
        self.experiment = stroop(self.use_develop_mode, self.start_time, screen_height, screen_width, True,
                                 self.outlet)
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        self.stress_evaluation_log = WriteToExcel("stress_evaluation_" + current_hour + "_" + current_min, "stress")
        self.cognitive_load_log = WriteToExcel("cognitive_load_evaluation_" + current_hour + "_" + current_min, "load")
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.condition = self.choose_condition()
        if self.condition != "Practice":
            self.choose_blocks_order()
            self.init_trials_orders()
        else:
            self.blocks_order = ["incong", "cong"]
            self.init_trials_orders()

        self.run_blocks();
        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()

    def init_trials_orders(self):
        index = 0
        for block in self.blocks_order:
            self.init_stimuli(block, index)
            index += 1

    def init_stimuli(self, block, index):
        locations = []
        directions = []
        minority_locations = numpy.random.choice(16, 4)
        locations_options = ["up", "down"]
        last_index = -1
        same_index_in_row = 0
        current_index = 0
        while current_index < 16:
            location_index = random.randint(0,1)
            locations.insert(current_index, locations_options[location_index])
            if last_index == location_index:
                if same_index_in_row >= 3:
                    continue
                else:
                    same_index_in_row += 1
            else:
                last_index = location_index
                same_index_in_row = 1
            current_index += 1

        minority_locations = numpy.sort(minority_locations)
        directions_options_congruent = {"up": "pointing_up", "down": "pointing_down"}
        directions_options_incongruent = {"up": "pointing_down", "down": "pointing_up"}
        index_in_minority_locations = 0
        index_in_locations = 0
        for location in locations:
            if index_in_minority_locations < 4 and \
                            index_in_locations == minority_locations[index_in_minority_locations]:
                if block == "incong":
                    directions.insert(index_in_locations, directions_options_congruent[location])
                else:
                    directions.insert(index_in_locations, directions_options_incongruent[location])
                index_in_minority_locations += 1
            else:
                if block == "incong":
                    directions.insert(index_in_locations, directions_options_incongruent[location])
                else:
                    directions.insert(index_in_locations, directions_options_congruent[location])

            index_in_locations += 1

        self.trials_directions_array.insert(index, directions)
        self.trials_locations_array.insert(index, locations)


    def choose_blocks_order(self):
        blocks_order = ['cong','cong', 'incong', 'incong' ]
        order_ok = False
        while order_ok == False:
            order_ok = True
            shuffle(blocks_order)
            same_in_row = 1
            index = 0
            for block in blocks_order:
                if index > 0 and block == blocks_order[index-1]:
                    same_in_row += 1
                    if same_in_row >= 3:
                        order_ok = False
                        break
                else:
                    same_in_row = 1
                index += 1

        self.blocks_order = blocks_order


    def choose_condition(self):
        condition = self.ask_for_condition()
        if condition == "practice":
            return "Practice"
        else:
            return "Task"

    def ask_for_condition(self):
        canvas = stimuli.BlankScreen()
        Practice = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_Practice = stimuli.TextLine(text="Practice", position=Practice.position,
                                 text_colour=misc.constants.C_WHITE)
        Test = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_Test = stimuli.TextLine(text="Test", position=Test.position,
                                 text_colour=misc.constants.C_WHITE)
        Practice.plot(canvas)
        text_Practice.plot(canvas)

        Test.plot(canvas)
        text_Test.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            _id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if Practice.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'practice'
            elif Test.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 'test'

    def run_blocks(self):
        block_index = 0
        for block in self.blocks_order:
            stay_on_block = True

            while stay_on_block:

                rest = RestBlock(self.outlet, exp = self.experiment.exp, use_pilot_mode = self.use_pilot_mode, \
                                 folder = self.instructions_folder, file = self.instructions_file)

                port = parallel.ParallelPort(address='0xE010')
                port.setData(1)
                stroop = self.experiment.run(block, self.condition, self.trials_locations_array[block_index], \
                                            self.trials_directions_array[block_index])
                port.setData(2)
                if self.condition == 'Practice':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    self.evaluate_stress(str(block[0]) + block[1])
                    self.evaluate_load(str(block[0]) + block[1])
                    stay_on_block = False
            block_index += 1

    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block, self.outlet)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block, self.outlet)