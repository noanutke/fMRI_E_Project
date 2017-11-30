from __future__ import division
from nback import Nback
from restBlock import RestBlock
from selfReport import SelfReport
from writeToExcel import WriteToExcel
from expyriment import control, stimuli, design, misc, io
import datetime

class runNbackTask:
    instructions_folder = "instructions_pilot_mode"
    use_pilot_mode = True
    use_develop_mode = True
    flight_simulator_mode = True
    blocks_practice = [(1, 'p', 'v'), (1, 'p', 'a'), (1, 'p')]
    blocks_no_stress = [(1, 'c'), (2, 'c'), (3, 'c')]
    blocks_sound = [(1, 'a'), (2, 'a'), (3, 'a')]
    blocks_pain = [(1, 'b'), (2, 'b'), (3, 'b')]
    for_miki = [(1, 'a'), (2, 'a'), (3, 'a')]
    tests = blocks_practice + blocks_no_stress
    block_to_run = blocks_practice + blocks_sound

    continue_key = misc.constants.K_SPACE
    repeat_block_key = misc.constants.K_0


    def __init__(self, screen_height, screen_width):
        self.start_time = datetime.datetime.now()
        self.experiment = Nback(self.use_develop_mode, self.start_time, screen_height, screen_width, True, False)
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
        for block in self.block_to_run:
            # if index > 2:
            # break
            stay_on_block = True
            stimuli_type = "both" if len(block) == 2 else block[2]
            block_type = block[1]
            with_stress = True if block_type == "a" else False

            n = block[0]
            while stay_on_block:

                if (block[0] == 1 and block_type == "c"):  # no stress
                    self.evaluate_stress(str(block[0]) + block[1] + "_before")

                rest = RestBlock(str(n), block_type, stimuli_type, self.experiment.exp, self.use_pilot_mode, \
                                 self.instructions_folder)

                n_back = self.experiment.run(n, block_type, stimuli_type)

                if block_type == 'p':
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True
                else:
                    self.evaluate_stress(str(block[0]) + block[1])
                    self.evaluate_load(str(block[0]) + block[1])

                if with_stress:
                    canvas = stimuli.BlankScreen()
                    feedback = "./pictures/feedback/" + str(n) + "_feedback.png"
                    feedback_picture = stimuli.Picture(feedback)
                    feedback_picture.plot(canvas)
                    canvas.present()
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    stay_on_block = False

                if self.use_pilot_mode == True:
                    text_title = stimuli.TextLine("Press space to start new block", (0, 0), text_size=(50))
                    canvas = stimuli.BlankScreen()
                    text_title.plot(canvas)
                    canvas.present()
                    key, rt = self.experiment.exp.keyboard.wait([self.continue_key, self.repeat_block_key])
                    if key is self.continue_key:
                        stay_on_block = False
                    else:
                        stay_on_block = True

    def evaluate_stress(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "stress", self.stress_evaluation_log, block)

    def evaluate_load(self, block):
        SelfReport(self.experiment.exp, self.screen_height, self.screen_width, \
                   "load", self.cognitive_load_log, block)