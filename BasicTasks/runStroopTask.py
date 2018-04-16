from __future__ import division
from stroop import stroop
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime
import random
from random import shuffle
import pandas as pd
import numpy
from psychopy import parallel
import utils

class runStroopTask:
    use_pilot_mode = True
    flight_simulator_mode = True

    instructions_folder = './pictures/instructions_stroop/'
    instructions_file = 'instructions.png'

    orders_path_prefix = "./ordersStroop/order";
    orders_path_suffix = ".csv"

    blocks_amount_in_condition = 4;
    trials_in_test_block = 16;
    trials_in_practice_block = 8;
    minority_trials_in_test_block = 4; # the amount of congruent trials in an incongruent block and vise versa
    minority_trials_in_practice_block = 2;  # the amount of congruent trials in an incongruent block and vise versa
    max_amount_of_same_stimuli_in_row = 3;
    max_amount_of_same_blocks_in_row = 3;
    is_practice = False;
    directions_options_congruent = {"up": "pointing_up", "down": "pointing_down"}
    directions_options_incongruent = {"up": "pointing_down", "down": "pointing_up"}
    locations_options = ["up", "down"]
    blocks_order = ['cong_a', 'cong_b', 'incong_a', 'incong_b']

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0
    exit_key = misc.constants.K_BACKSPACE

    def __init__(self, screen_height, screen_width, exp, subNumber, outlet):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.subNumber = subNumber
        self.exp = exp
        self.fixationTimes = [6,6,3,9]  # Array of fixation time for each block - the average of the array is 6
        random.shuffle(self.fixationTimes)

        self.current_block_order_number = "";    # block order (1-4)
        self.blocks_order = []  # blocks array
        self.trials_locations_array = []    #arrow locations lists for all blocks
        self.trials_directions_array = []   #arrow direction lists for all blocks

        self.outlet = outlet # LSL stream

        # init stroop class
        self.experiment = stroop(self.exp, self.outlet, self.subNumber)

        # create stress and load self reports files
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        self.stress_evaluation_log = WriteToExcel("stress_evaluation_stroop" + self.subNumber + "_" + current_hour + "_" + current_min, "stress")
        self.cognitive_load_log = WriteToExcel("cognitive_load_evaluation_stroop" + self.subNumber + "_" + current_hour + "_" + current_min, "load")

        self.start_again = True #should choose condition (practice/test) again
        utils.push_sample_current_time(self.outlet, ["startTask_task_stroop"] )


    def init_stimuli_from_file(self):
        index = 0
        for block in self.blocks_order:

            # Load spreadsheet
            xl = pd.read_csv(self.orders_path_prefix + self.current_block_order_number + "_" + block + \
                             self.orders_path_suffix, header=None)
            directions = [] # array of that holds arrow directions a block
            locations = []  # array of that holds arrow locations a block

            for value in range(0,self.trials_in_test_block):
                directions.insert(len(directions), xl[value][0])
                locations.insert(len(directions), xl[value][1])

            self.trials_directions_array.insert(index, directions)
            self.trials_locations_array.insert(index, locations)
            index += 1;

    # run stroop task
    def start_run(self):
        start_new_exp = False   # we want to start a new experiemnt (new log files) only when we
                                # finished to whole nBack task
        while self.start_again == True:
            self.start_again = False
            self.condition = self.choose_condition()    #choose if test or practice
            if self.condition == "exit":
                break
            if self.condition != "practice":
                self.ask_for_order()
                self.is_practice = False

                #############   Normaly we only initiate blocks from files  #################
                #self.choose_blocks_order(self.current_block_order_number)
                #self.init_trials_orders(True, self.current_block_order_number)

                self.init_blocks_order_from_file()
                self.init_stimuli_from_file()
            else: # we are in a practice block
                self.is_practice = True
                self.blocks_order = ["incong"]  # for practice we always use incongruent block
                self.init_trials_orders(False, "", True)

            start_new_exp = self.run_blocks();

        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()
        return start_new_exp

    def init_blocks_order_from_file(self):
        # Load spreadsheet
        xl = pd.read_csv(self.orders_path_prefix + self.current_block_order_number + ".csv")
        #df1 = xl.parse("Sheet1")
        self.blocks_order = []
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

    # this function initialize the trials list
    def init_trials_orders(self, init_file, order, isPractice = False):
        index = 0
        for block in self.blocks_order:
            self.init_stimuli(block, index, init_file, order, isPractice)
            index += 1

    def init_stimuli(self, block, index, init_file, order, isPractice):
        locations = []
        directions = []
        minority_amount = self.minority_trials_in_test_block;
        trials_amount = self.trials_in_test_block;
        if (isPractice == True):
            minority_amount = self.minority_trials_in_practice_block
            trials_amount = self.trials_in_practice_block

        # choose indices for minority locations
        minority_indices = numpy.random.choice(trials_amount, minority_amount)

        last_index = -1
        same_index_in_row = 1
        current_index = 0
        # choose locations for arrows
        while current_index < trials_amount:
            location_index = random.randint(0,1)
            locations.insert(current_index, self.locations_options[location_index])
            if last_index == location_index:
                if same_index_in_row >= self.max_amount_of_same_stimuli_in_row:
                    continue
                else:
                    same_index_in_row += 1
            else:
                last_index = location_index
                same_index_in_row = 1
            current_index += 1

        minority_indices = numpy.sort(minority_indices)

        index_in_minority_indices = 0
        index_in_locations = 0
        for location in locations:
            # check if this index is a minority index (incongruent trial in a congruent block or vise versa)
            if index_in_minority_indices < minority_amount and \
                            index_in_locations == minority_indices[index_in_minority_indices]:
                if block == "incong":
                    directions.insert(index_in_locations, self.directions_options_congruent[location])
                else:
                    directions.insert(index_in_locations, self.directions_options_incongruent[location])
                    index_in_minority_indices += 1
            else:   # we get here if this index in not a minority index
                if block == "incong":
                    directions.insert(index_in_locations, self.directions_options_incongruent[location])
                else:
                    directions.insert(index_in_locations, self.directions_options_congruent[location])

            index_in_locations += 1

        self.trials_directions_array.insert(index, directions)
        self.trials_locations_array.insert(index, locations)

        if init_file != True:
            self.trials_locations_array.insert(index, locations)
        else:   # we should init orders files.
            excel_writer = WriteToExcel(self.orders_path_prefix + order + "_" + str(self.blocks_order[index]), None)
            excel_writer.add_row(directions)
            excel_writer.add_row(locations)
            excel_writer.close_file()


    # this function chooses blocks order and write them to file
    def choose_blocks_order(self, order):
        order_ok = False
        while order_ok == False:
            order_ok = True
            shuffle(self.blocks_order)
            same_in_row = 1
            index = 0
            for block in (self.blocks_order):
                if index > 0 and block == (self.blocks_order[index-1]):
                    same_in_row += 1
                    if same_in_row >= self.max_amount_of_same_stimuli_in_row:
                        order_ok = False
                        break
                else:
                    same_in_row = 1
                index += 1

        excel_writer = WriteToExcel(self.orders_path_prefix + order, None)
        excel_writer.add_row(self.blocks_order)
        excel_writer.close_file()


    def choose_condition(self):
        condition = self.ask_for_condition()
        if condition == "practice":
            return "practice"
        elif condition == "test":
            return "test"
        else:
            return "exit"

    def ask_for_condition(self):
        canvas = stimuli.BlankScreen()
        Practice = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_Practice = stimuli.TextLine(text="Practice", position=Practice.position,
                                 text_colour=misc.constants.C_WHITE)
        Test = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_Test = stimuli.TextLine(text="Test", position=Test.position,
                                 text_colour=misc.constants.C_WHITE)

        exit = stimuli.Rectangle(size=(100, 80), position=(0, -200))
        text_exit = stimuli.TextLine(text="Exit", position=exit.position,
                                 text_colour=misc.constants.C_WHITE)

        Practice.plot(canvas)
        text_Practice.plot(canvas)

        Test.plot(canvas)
        text_Test.plot(canvas)

        exit.plot(canvas)
        text_exit.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            _id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if Practice.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'practice'
            elif Test.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'test'
            elif exit.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'exit'

    def run_blocks(self):
        block_index = 0
        evaluate_stress_first_time = False
        for block in self.blocks_order:
            stay_on_block = True

            while stay_on_block:
                if self.is_practice != True and evaluate_stress_first_time == False:
                    # we are in a test condition and haven't show the stress self evaluation yet
                    # so we should show it now
                    self.evaluate_stress(str(block))
                    evaluate_stress_first_time = True

                # show instructions and fixation
                rest = RestBlock("stroop", self.outlet, self.fixationTimes[block_index],\
                                 instructions_path= self.instructions_folder + self.instructions_file,\
                                 exp = self.experiment.exp, is_practice=self.is_practice)
                cont = rest.start_rest();

                # if the user pressed backspace  - we want to break but don'tt start a new experiment
                # just go back to the choose task screen
                if cont == False:
                    return False

                port = parallel.ParallelPort(address='0xE010')
                # send start block trigger
                port.setData(int(20 + block_index + 1))

                stroop = self.experiment.run(block, self.is_practice, self.trials_locations_array[block_index], \
                                            self.trials_directions_array[block_index],
                                             self.current_block_order_number, block_index)
                # send end block trigger
                port.setData(int(200))

                block_index += 1
                # if we are in a practice block - we wait for the user's input to decide what to do
                if self.is_practice:
                    self.start_again = True
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key, \
                                                                 self.exit_key])

                    if key is self.exit_key:
                        return False
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    # check if we are at the end of the condition ot at the middle of the condition
                    if block_index == self.blocks_amount_in_condition / 2 \
                            or block_index == self.blocks_amount_in_condition:
                        self.evaluate_stress(str(block[0]) + block[1])
                        self.evaluate_load(str(block[0]) + block[1])
                    stay_on_block = False
        return True

    def evaluate_stress(self, block):
        return SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, self.outlet, self.subNumber,\
                   self.current_block_order_number, "stroop")

    def evaluate_load(self, block):        return SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, self.outlet, self.subNumber,\
                   self.current_block_order_number, "stroop")
