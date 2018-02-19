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

    def init_stimuli_from_file(self):

        index = 0
        for block in self.blocks_order:

            # Load spreadsheet
            xl = pd.read_csv("./ordersStroop/order" + self.current_block_order_number + "_" + block + ".csv", header=None)
            directions = []
            locations = []

            for value in range(0,16):
                directions.insert(len(directions), xl[value][0])
                locations.insert(len(directions), xl[value][1])

            self.trials_directions_array.insert(index, directions)
            self.trials_locations_array.insert(index, locations)
            index += 1;

    def __init__(self, screen_height, screen_width, exp, use_develop_mode):
        self.use_develop_mode = use_develop_mode
        self.exp = exp
        self.fixationTimes = [6,6,3,9]
        random.shuffle(self.fixationTimes)

        self.current_block_order_number = "";
        self.blocks_order = []
        self.trials_locations_array = []
        self.trials_directions_array = []
        shuffle(self.allBlocks)
        info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'myuidw43536')
        self.outlet = StreamOutlet(info)
        self.start_time = datetime.datetime.now()
        self.experiment = stroop(self.exp, self.start_time, screen_height, screen_width, True,
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
            if self.condition != "Practice":
                self.ask_for_order()

                #self.choose_blocks_order(self.current_block_order_number)
                #self.init_trials_orders(True, self.current_block_order_number)

                self.init_blocks_order_from_file()
                self.init_stimuli_from_file()
            else:
                self.blocks_order = ["incong", "cong"]
                self.init_trials_orders(False, "")

            self.run_blocks();
            self.stress_evaluation_log.close_file()
            self.cognitive_load_log.close_file()

    def init_blocks_order_from_file(self):
        # Load spreadsheet
        xl = pd.read_csv("./ordersStroop/order" + self.current_block_order_number + ".csv")
        #df1 = xl.parse("Sheet1")

        for values in xl:
            self.blocks_order.insert(len(self.blocks_order), values)

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

    def init_trials_orders(self, init_from_file, order):
        index = 0
        for block in self.blocks_order:
            self.init_stimuli(block, index, init_from_file, order)
            index += 1

    def init_stimuli(self, block, index, init_from_file, order):
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

        if init_from_file != True:
            self.trials_locations_array.insert(index, locations)
        else:
            excel_writer = WriteToExcel("./ordersStroop/order" + order + "_" + str(self.blocks_order[index]), None)
            excel_writer.add_row(directions)
            excel_writer.add_row(locations)
            excel_writer.close_file()


    def choose_blocks_order(self, order):
        blocks_order = ['cong_a','cong_b', 'incong_a', 'incong_b' ]
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
        excel_writer = WriteToExcel("./ordersStroop/order" + order, None)
        excel_writer.add_row(blocks_order)
        excel_writer.close_file()


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

            evaluate_stress_first_time = False
            while stay_on_block:
                if self.condition != 'Practice' and evaluate_stress_first_time == False:
                    self.evaluate_stress(str(block))
                    evaluate_stress_first_time = True

                rest = RestBlock(self.outlet, self.fixationTimes[block_index],
                                 exp = self.experiment.exp, use_pilot_mode = self.use_pilot_mode, \
                                 folder = self.instructions_folder, file = self.instructions_file)

                port = parallel.ParallelPort(address='0xE010')
                port.setData(int(1))
                stroop = self.experiment.run(block, self.condition, self.trials_locations_array[block_index], \
                                            self.trials_directions_array[block_index])
                port.setData(int(2))
                if self.condition == 'Practice':
                    self.start_again = True
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    if block_index == 1 or block_index == 3:
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