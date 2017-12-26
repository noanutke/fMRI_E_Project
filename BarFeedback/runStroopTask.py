from __future__ import division
from stroop import stroop
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime
from random import shuffle
from pylsl import StreamInfo, StreamOutlet

class runStroopTask:
    instructions_folder = "instructions_pilot_mode"
    use_pilot_mode = True
    use_develop_mode = True
    flight_simulator_mode = True

    folder = './NewStroop'
    instructions_folder = 'NewStroop/instructions'
    instructions_file = 'instructions.png'

    allBlocks = ['high', 'low', 'medium', 'baseline','high', 'low', 'medium', 'baseline',\
                 'high', 'low', 'medium', 'baseline']

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width):
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

        self.run_blocks();
        self.stress_evaluation_log.close_file()
        self.cognitive_load_log.close_file()

    def run_blocks(self):
        for block in self.allBlocks:
            # if index > 2:
            # break
            stay_on_block = True
            stimuli_type = "both" if len(block) == 2 else block[2]
            block_type = block[1]
            with_stress = True if block_type == "a" else False

            while stay_on_block:

                rest = RestBlock(self.outlet, exp = self.experiment.exp, use_pilot_mode = self.use_pilot_mode, \
                                 folder = self.instructions_folder, file = self.instructions_file)

                n_back = self.experiment.run(block)

                if block == 'p':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    self.evaluate_stress(str(block[0]) + block[1])
                    self.evaluate_load(str(block[0]) + block[1])

    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block, self.outlet)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block, self.outlet)