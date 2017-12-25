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

class runNbackTask:
    instructions_folder = "instructions_pilot_mode_new"
    use_pilot_mode = True
    use_develop_mode = True
    flight_simulator_mode = True
    '''
    blocks_practice = [(1, 'p', 'v'), (1, 'p', 'a'), (1, 'p')]
    blocks_no_stress = [(1, 'c'), (2, 'c'), (3, 'c')]
    blocks_sound = [(1, 'a'), (2, 'a'), (3, 'a')]
    blocks_baseline= [(4, 'baseline'), (5, 'baseline')]
    blocks_pain = [(1, 'b'), (2, 'b'), (3, 'b')]
    for_miki = [(1, 'a'), (2, 'a'), (3, 'a')]
    tests = blocks_practice + blocks_no_stress
    block_to_run = blocks_practice + blocks_baseline + blocks_sound
    '''

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width):
        self.is_baseline = False
        self.blocks_order = []
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
        else:
            self.blocks_order = ["Sheet1", "Sheet1", "Sheet1"]

        self.run_blocks();
        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()

    def choose_blocks_order(self):
        order_number = self.ask_for_order()
        # Assign spreadsheet filename to `file`
        file = './orders.xlsx'

        # Load spreadsheet
        xl = pd.ExcelFile(file)
        df1 = xl.parse("Sheet1")

        blocks_amount = 11
        for values in df1.values:
            if blocks_amount == 0:
                break
            self.blocks_order.insert(len(self.blocks_order), values[order_number])
            blocks_amount-=1


    def choose_condition(self):
        condition = self.ask_for_condition()
        if condition == "practice":
            return "BlockProtocol_Practice"
        elif condition == "stress":
            return "BlockProtocol_Stress"
        else:
            return "BlockProtocol_NoStress"

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
            _id, pos, _rt = self.experiment.exp.mouse.wait_press()

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

    def ask_for_order(self):
        canvas = stimuli.BlankScreen()
        order1 = stimuli.Rectangle(size=(100, 80), position=(-200, 0))
        text_order1 = stimuli.TextLine(text="Order1", position=order1.position,
                                         text_colour=misc.constants.C_WHITE)
        order2 = stimuli.Rectangle(size=(100, 80), position=(200, 0))
        text_order2 = stimuli.TextLine(text="Order2", position=order2.position,
                                      text_colour=misc.constants.C_WHITE)

        order3 = stimuli.Rectangle(size=(100, 80), position=(-200, -200))
        text_order3 = stimuli.TextLine(text="Order3", position=order3.position,
                                             text_colour=misc.constants.C_WHITE)

        order4 = stimuli.Rectangle(size=(100, 80), position=(200, -200))
        text_order4 = stimuli.TextLine(text="Order4", position=order4.position,
                                             text_colour=misc.constants.C_WHITE)

        order1.plot(canvas)
        text_order1.plot(canvas)

        order2.plot(canvas)
        text_order2.plot(canvas)

        order3.plot(canvas)
        text_order3.plot(canvas)

        order4.plot(canvas)
        text_order4.plot(canvas)

        self.experiment.exp.mouse.show_cursor()
        canvas.present()

        while True:
            _id, pos, _rt = self.experiment.exp.mouse.wait_press()

            if order1.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 0
            elif order2.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                self.use_develop_mode = False
                return 1
            elif order3.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 2
            elif order4.overlapping_with_position(pos):
                self.experiment.exp.mouse.hide_cursor()
                return 3

    def run_blocks(self):
        evaluate_stress_first_time = False
        practice_block = 0
        for block in self.blocks_order:
            n = block[0]
            self.is_baseline = False
            if n == '0':
                self.is_baseline = True
                if block[7] == 'a':
                    n='4'
                else:
                    n='5'
            # if index > 2:
            # break
            stay_on_block = True
            stimuli_type = "both"

            block_type = ""
            if self.condition == "BlockProtocol_Practice":
                n = '1'
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
                    self.evaluate_stress(str(block[0]) + block[1] + "_before")
                    evaluate_stress_first_time = True

                if self.is_baseline == True: #baseline
                    rest = RestBlock(self.outlet, str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     "", "./pictures/"+\
                                     self.instructions_folder + "/Slide" + str(n) + "_baseline.png")
                else:
                    rest = RestBlock(self.outlet, str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                     self.instructions_folder)

                n_back = self.experiment.run(n, block_type, stimuli_type, block, self.condition, self.is_baseline)

                if block_type == 'p':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    stay_on_block = False
                    self.evaluate_stress(str(block[0]) + "_" + self.condition)
                    self.evaluate_load(str(block[0]) + "_" + self.condition)

                '''
                if self.condition == "stress":
                    canvas = stimuli.BlankScreen()
                    feedback = "./pictures/feedback/" + str(n) + "_feedback.png"
                    feedback_picture = stimuli.Picture(feedback)
                    feedback_picture.plot(canvas)
                    canvas.present()
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    stay_on_block = False
                '''


    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block, self.outlet)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block, self.outlet)