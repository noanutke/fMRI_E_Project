from __future__ import division
from nback import Nback
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime
import random
import pandas as pd
from psychopy import parallel

class runNbackTask:
    instructions_folder = "./pictures/instructions_nBack"
    instructions_prefix = "slide"
    instructions_suffix = ".png"

    orders_path_prefix = "./ordersNback/order";
    orders_path_suffix = ".csv"

    stress_evaluation_file_prefix = "stress_evaluation_nback";
    load_evaluation_file_prefix = "cognitive_load_evaluation_nback";

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0
    exit_key = misc.constants.K_BACKSPACE

    baseline_target_a = "4";
    baseline_target_b = "5";
    targets_amount_in_block = 4;
    trials_amount_in_block = 12;
    maximum_amount_of_targets_in_row = 2;
    maximum_amount_of_same_stimulus_in_row = 3;
    blocks_amount_in_condition = 8;

    def __init__(self, screen_height, screen_width, exp, subNumber, outlet):
        self.n = "";    # nLevel
        self.outlet = outlet;   # LSL stream
        self.stimuli_type = "" # practice type: auditory(a) / visual(b) / both
        self.subNumber = subNumber  # subject number
        self.exp = exp
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.is_practice = False

        self.fixationTimes = [6,6,9,9,9,3,3,3]  # fixation times array
        random.shuffle(self.fixationTimes)

        self.is_baseline = False   # is this a baseline block (nLevel = 0)
        self.current_block_order_number = ""    # block order (1-4)
        self.blocks_order = []  # blocks array
        self.letters_lists = [""]   #letters lists for all blocks
        self.locations_lists = [""] #locations list for all blocks

        # init Nback class
        self.experiment = Nback(self.exp, self.outlet, self.subNumber)

        # create stress and load self reports files
        current_hour = str(datetime.datetime.now().hour)
        current_min = str(datetime.datetime.now().minute)
        self.stress_evaluation_log = WriteToExcel(self.stress_evaluation_file_prefix + \
                                                  self.subNumber + "_" + current_hour + "_" + current_min, "stress")
        self.cognitive_load_log = WriteToExcel(self.load_evaluation_file_prefix + \
                                               self.subNumber + "_" + current_hour + "_" + current_min, "load")

        self.outlet.push_sample(["startTask_task_nBack"])   #send start task trigger to LSL

    # run nBack task
    def start_run(self):
        start_new_exp = False   # we want to start a new experiemnt (new log files) only when we
                                # finished to whole nBack task

        self.condition = self.choose_condition() #choose if test or practice
        if self.condition == "exit":
            return start_new_exp
        if self.condition != "BlockProtocol_Practice":
            self.ask_for_order()
            self.is_practice = False;

            #############   Normaly we only initiate blocks from files  #################
            #self.choose_blocks_order(self.current_block_order_number)
            #self.init_trials_lists(True, self.current_block_order_number)

            self.init_blocks_order_from_file()
            self.init_stimuli_from_file()
            self.stimuli_type = "both";

        else:   # we are in a practice block
            self.is_practice = True
            self.n = self.ask_for_level()   # ask for nLevel
            self.stimuli_type = self.ask_for_practice_type()   # ask for practice type (auditory/visual/both)
            self.blocks_order = [self.n + "_a"] # for practice blocks we will always use "a" types
            self.init_trials_lists(False, "")

        start_new_exp = self.run_blocks();

        # we finished running all of the blocks so we need to close the self evaluation files
        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()
        return start_new_exp

    # Init blocks_order array to contain the blocks names in the right order
    def init_blocks_order_from_file(self):
        xl = pd.read_csv(self.orders_path_prefix + self.current_block_order_number + self.orders_path_suffix)
        self.blocks_order = []
        for values in xl:
            self.blocks_order.insert(len(self.blocks_order), values)

    # this function initialize the trials list
    def init_trials_lists(self, init_to_file, order=""):
        baseline_target = -1

        for i in range(len(self.blocks_order)):
            nLevel = int(self.blocks_order[i].split('_')[0])
            type = self.blocks_order[i].split('_')[1]

            if nLevel == 0:
                if type == "a":
                    baseline_target = self.baseline_target_a
                else:
                    baseline_target= self.baseline_target_b

            rand = random.randint(1,2)
            letters_targets_amount = 0
            locations_targets_amount = 0
            if self.stimuli_type == "a":
                letters_targets_amount = self.targets_amount_in_block
            elif self.stimuli_type == "v":
                locations_targets_amount = self.targets_amount_in_block
            else:
                if rand == 1:   # we should have 1 dual target, so we randomly choose which modality has
                                # more targets (since it won't be equal if we demand 4 targets total)
                    letters_targets_amount = 2
                    locations_targets_amount = 3
                else:
                    letters_targets_amount = 3
                    locations_targets_amount = 2

            location_target_index = -1  # the index of the dual target - so we demand that a location target
                                        # will be there
            letters_targets_indices =  []
            if self.stimuli_type != "v":   # we have auditory stimuli - so we initialize the targets for them
                letters_lists, location_target_index, letters_targets_indices = self.generate_trials\
                    (nLevel, letters_targets_amount, baseline_target, -1, [])
            if self.stimuli_type != "a":   # we have visual stimuli - so we initialize the targets for them
                locations_lists, index, locations_targets_indices = self.generate_trials\
                    (nLevel, locations_targets_amount, baseline_target, location_target_index, letters_targets_indices)

            if init_to_file != True:
                if self.stimuli_type != "v":
                    self.letters_lists.insert(i, letters_lists)
                if self.stimuli_type != "a":
                    self.locations_lists.insert(i, locations_lists)
            else:
                excel_writer = WriteToExcel(self.orders_path_prefix + order + "_" + str(self.blocks_order[i]), None)
                excel_writer.add_row(letters_lists)
                excel_writer.add_row(locations_lists)
                excel_writer.close_file()


    def init_stimuli_from_file(self):
        index = 0
        for block in self.blocks_order:

            # Load spreadsheet
            xl = pd.read_csv(self.orders_path_prefix + self.current_block_order_number + "_" \
                             + block + self.orders_path_suffix, header=None)
            letters = []
            locations = []

            for value in range(0,self.trials_amount_in_block):
                letters.insert(len(letters), xl[value][0])
                locations.insert(len(letters), xl[value][1])

            self.letters_lists.insert(index, letters)
            self.locations_lists.insert(index, locations)
            index += 1;


    def choose_blocks_order(self, order):
        # we make sure that each half contains all block types (in a random order)
        blocks1 = ["0_a","1_a","2_a","3_a"]
        blocks2 = ["0_b","1_b","2_b","3_b"]
        random.shuffle(blocks1)
        random.shuffle(blocks2)
        blocks1.extend(blocks2)
        self.blocks_order = blocks1
        excel_writer = WriteToExcel(self.orders_path_suffix + order, None)
        excel_writer.add_row(blocks1)
        excel_writer.close_file()

    # choose condition: practice / test
    def choose_condition(self):
        condition = self.ask_for_condition()
        if condition == "practice":
            return "BlockProtocol_Practice"
        elif condition == "test":
            return "test"
        else:
            return "exit"

    # check if targets demand are satisfied - no more than maximum_amount_of_targets_in_row in a row
    def check_if_target_demands_ok(self, indices):
        target_in_row = 1
        i = 0
        for index in indices:
            if i == 0:
                i += 1
                continue
            if index == indices[i-1] + 1:
                target_in_row += 1
                if target_in_row > self.maximum_amount_of_targets_in_row:
                    return False
            else:
                target_in_row = 1
        return True

    # make sure that there are no more than maximum_amount_of_same_stimulus_in_row in a row
    def check_if_trials_order_ok(self, trials):
        same_in_row = 1
        i = 0
        for trial in trials:
            if i == 0:
                i+=1;
                continue
            if trial == trials[i-1]:
                same_in_row += 1
                if same_in_row > self.maximum_amount_of_same_stimulus_in_row:
                    return False
            else:
                same_in_row = 1
            i+=1
        return True


    def generate_trials(self, n, targets_amount_required, baseline_target, dual_target_index, other_modality_targets):
        target_demands_ok = False
        # try to choose target indices as long as target demands aren't satisfied
        while target_demands_ok == False:
            target_indices = []
            targets_amount_corrected = targets_amount_required
            if dual_target_index > -1:  # we have a demand ro place a target in a specific index
                                        # for the creation of the dual target
                target_indices.insert(0, dual_target_index)
                targets_amount_corrected -= 1

            # randomly choose target indices
            targetsAmount = 0;
            while targetsAmount < targets_amount_corrected:
                index = random.randint(n,11)    # lowest index possible is nLevel

                # we check that th chosen index is not already in our indices and not in
                # other modality targets (we don't want to have an extra dual target - only one)
                if index in target_indices or (index in other_modality_targets):
                    continue

                target_indices.insert(0, index)
                targetsAmount += 1 ;

            if self.check_if_target_demands_ok(target_indices):
                target_demands_ok = True


        target_indices.sort()
        trials_order_ok = False
        # now we randomly choose stimuli
        while trials_order_ok == False:
            trials = []
            target_index = 0
            for i in range(self.trials_amount_in_block):
                # check if this index is a target index
                if target_index < len(target_indices) and target_indices[target_index] == i:
                    target_index += 1
                    if n == 0:
                        trials.insert(i, baseline_target)
                    else:
                        trials.insert(i, trials[i-n])

                else:   # this is not a target index
                    trial = random.randint(1,8)
                    # define the value to exclude - which value we should not give to the stimuli so
                    # we don't have a target in this index
                    value_to_exclude = baseline_target
                    if n != 0 and i-n >= 0:
                        value_to_exclude = trials[i-n]
                    # if we randomly chosen the forbidden stimulus - we simply choose the next possible stimulus
                    if trial == value_to_exclude:
                        trial += 1
                    if trial > 8:
                        trial = 1

                    trials.insert(i, trial)

            if self.check_if_trials_order_ok(trials):
                trials_order_ok = True

        # choose one of this modality's target to be the dual target (this will only be relevant
        if (dual_target_index == -1):
            dual_target_index = target_indices[random.randint(0, len(target_indices)-1)]
        return (trials, dual_target_index, target_indices)

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
        level2 = stimuli.Rectangle(size=(100, 80), position=(0, 0))
        text_level2 = stimuli.TextLine(text="2 back", position=level2.position,
                                 text_colour=misc.constants.C_WHITE)

        level3 = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
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


    def ask_for_practice_type(self):
        canvas = stimuli.BlankScreen()
        auditory = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_auditory = stimuli.TextLine(text="auditory", position=auditory.position,
                                 text_colour=misc.constants.C_WHITE)
        spatial = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_spatial = stimuli.TextLine(text="spatial", position=spatial.position,
                                 text_colour=misc.constants.C_WHITE)

        both = stimuli.Rectangle(size=(100, 80), position=(0, 0))
        text_both = stimuli.TextLine(text="both", position=both.position,
                                 text_colour=misc.constants.C_WHITE)


        auditory.plot(canvas)
        text_auditory.plot(canvas)

        spatial.plot(canvas)
        text_spatial.plot(canvas)

        both.plot(canvas)
        text_both.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if auditory.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "a"
            elif spatial.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "v"
            elif both.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return "both"

    def ask_for_condition(self):
        canvas = stimuli.BlankScreen()
        Practice = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_Practice = stimuli.TextLine(text="Practice", position=Practice.position,
                                 text_colour=misc.constants.C_WHITE)
        Basic = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_Basic = stimuli.TextLine(text="Test", position=Basic.position,
                                 text_colour=misc.constants.C_WHITE)

        exit = stimuli.Rectangle(size=(100, 80), position=(0, -200))
        text_exit = stimuli.TextLine(text="Exit", position=exit.position,
                                 text_colour=misc.constants.C_WHITE)


        Practice.plot(canvas)
        text_Practice.plot(canvas)

        Basic.plot(canvas)
        text_Basic.plot(canvas)

        exit.plot(canvas)
        text_exit.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if Practice.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'practice'
            elif Basic.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'test'
            elif exit.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 'exit'

    def run_blocks(self):
        evaluate_stress_first_time = False
        block_index = 0
        for block in self.blocks_order:
            self.n = int(block.split('_')[0])
            block_type = block.split('_')[1]    # "a" or "b"
            self.is_baseline = False

            stay_on_block = True
            if self.n == 0:
                self.is_baseline = True
                if block_type == 'a':
                    self.n = self.baseline_target_a;
                else:
                    self.n = self.baseline_target_b;

            while stay_on_block:

                if self.is_practice != True and evaluate_stress_first_time == False:
                    # we are not in practice and we didn't show the first stress evaluation
                    self.evaluate_stress(str(block))
                    evaluate_stress_first_time = True

                instructions_path = self.get_instructions_path()

                # show instructions and fixation
                rest = RestBlock("nBack", self.outlet, self.fixationTimes[block_index], \
                                 instructions_path, self.experiment.exp, self.is_practice)
                cont = rest.start_rest();

                # if the user pressed backspace  - we want to break but don'tt start a new experiment
                # just go back to the choose task screen
                if cont == False:
                    return False;

                port = parallel.ParallelPort(address='0xE010')
                # send start block trigger
                port.setData(int(10 + block_index + 1))

                self.experiment.run(self.n, self.letters_lists[block_index], self.locations_lists[block_index], \
                                    self.is_practice, self.stimuli_type, self.is_baseline, \
                                             self.current_block_order_number,block_index)

                # send end block trigger
                port.setData(int(100))

                # if we are in a practice block - we wait for the user's input to decide what to do
                if self.is_practice:
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key,\
                                                                 self.exit_key])
                    if key is self.repeat_block_key:
                        stay_on_block = True
                    else:
                        return False;   # go to choose task screen again
                else:
                    block_index += 1
                    stay_on_block = False

                    # check if we are at the end of the condition ot at the middle of the condition
                    if block_index ==self.blocks_amount_in_condition / 2 \
                            or block_index == self.blocks_amount_in_condition:
                        self.evaluate_stress(str(block) + "_" + self.condition)
                        self.evaluate_load(str(block) + "_" + self.condition)
        return True


    def get_instructions_path(self):
        instructions = "";
        if self.is_baseline:
            instructions = self.instructions_folder + "/" + self.instructions_prefix + str(self.n) + "_baseline"
        else:
            instructions = self.instructions_folder + "/" + self.instructions_prefix + str(self.n)
            if self.is_practice:
                instructions = instructions + "_" + "p"
                instructions = instructions + "_" + self.stimuli_type

        instructions = instructions + ".png"
        return instructions;

    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, self.outlet, self.subNumber, \
                   self.current_block_order_number, "nBack")

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, self.outlet, self.subNumber,\
                   self.current_block_order_number, "nBack")