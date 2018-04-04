from expyriment import control, stimuli, design, misc, io
import pandas as pd
import time as Time

class RestBlock:
    continue_key = misc.constants.K_SPACE
    exit_key = misc.constants.K_BACKSPACE
    show_instructions_for_seconds = 9
    show_cross_for_seconds = 1

    def __init__(self, task, lsl_stream, fixationTime, next_block="", block_type="", stimuli_type="",
                 exp=None, use_pilot_mode=False,\
                 folder="", file = ""):
        self.task = task;
        self.show_cross_for_seconds = fixationTime;
        self.use_pilot_mode = use_pilot_mode
        self.next_block = next_block
        self.canvas = stimuli.BlankScreen()
        self.exp = exp
        self.folder = folder
        self.file = file
        self.lsl_stream = lsl_stream
        self.block_type = block_type
        self.task = task
        self.stimuli_type = stimuli_type
        self.next_block = next_block

    def start_rest(self):

        self.lsl_stream.push_sample(["instructions_start_1_task_" + self.task])
        cont = self.write_anticipation_text(self.next_block, self.block_type, self.stimuli_type, self.exp)

        self.lsl_stream.push_sample(["instructions_end_1_task_" + self.task])
        if cont == False:
            return False
        if self.block_type == 'p':
            return True;
        else:
            self.lsl_stream.push_sample(["fixation_start_1_task_" + self.task])
            cont = self.paint_cross(self.exp)
            self.lsl_stream\
                .push_sample(["fixation_end_1_task_" + self.task])
            if cont == True:
                return True
            return False

    def paint_cross(self, exp):
        start_block_time = Time.time()
        self.canvas = stimuli.BlankScreen()
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        cross.plot(self.canvas)
        self.canvas.present()
        key, rt = exp.keyboard.wait([self.exit_key], self.show_cross_for_seconds * 1000)
        if key is self.exit_key:
            return False
        end_block_time = Time.time()
        return True


    def write_anticipation_text(self, n, block_type, stimuli_type, exp):

        start_block_time = Time.time()
        self.canvas = stimuli.BlankScreen()

        self.plot_instructions(n, block_type, stimuli_type)
        self.canvas.present()
        if block_type == "p":
            key, rt = self.exp.keyboard.wait([self.continue_key,\
                                              self.exit_key], self.show_instructions_for_seconds * 1000)
            if key is self.continue_key:
                return True
            elif key is self.exit_key:
                return False

        else:
            key, rt = exp.keyboard.wait([self.exit_key], self.show_instructions_for_seconds * 1000)
            if key is self.exit_key:
                return False
            end_block_time = Time.time()
            print('noa')
            return True


    def plot_instructions(self, n, block_type, stimuli_type):
        instructions = ""
        if self.file != "" and self.folder != "":
            instructions = "./" + self.folder + "/" + self.file
        elif self.file != "" and self.folder == "":
            instructions = self.file
        else:
            instructions = "./pictures/"+ self.folder + "/Slide" + n
            if block_type == 'p':
                instructions = instructions + "_" + block_type
                if stimuli_type != None:
                    instructions = instructions + "_" + stimuli_type
            instructions = instructions + ".png"

        instruction_picture = stimuli.Picture(instructions)
        instruction_picture.plot(self.canvas)
