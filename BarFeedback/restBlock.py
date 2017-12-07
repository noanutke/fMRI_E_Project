from expyriment import control, stimuli, design, misc, io
import pandas as pd


class RestBlock:
    continue_key = misc.constants.K_SPACE
    show_instructions_for_seconds = 3
    show_cross_for_seconds = 1

    def __init__(self, next_block="", block_type="", stimuli_type="", exp=None, use_pilot_mode=False,\
                 folder="", file = ""):
        self.use_pilot_mode = use_pilot_mode
        self.next_block = next_block
        self.canvas = stimuli.BlankScreen()
        self.exp = exp
        self.folder = folder
        self.file = file

        self.paint_cross(exp)
        self.write_anticipation_text(next_block, block_type, stimuli_type, exp)

    def paint_cross(self, exp):
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        cross.plot(self.canvas)
        self.canvas.present()
        exp.clock.wait(self.show_cross_for_seconds*1000)


    def write_anticipation_text(self, n, block_type, stimuli_type, exp):
        self.canvas = stimuli.BlankScreen()

        if self.use_pilot_mode:
            self.plot_instructions(n, block_type, stimuli_type)
            self.canvas.present()
            key, rt = self.exp.keyboard.wait([self.continue_key])
            return

        time_left = self.show_instructions_for_seconds
        while time_left > 0:
            self.plot_instructions(n, block_type, stimuli_type)

            time = stimuli.TextBox(str(time_left), [200,200], [0,-280], None, 40)
            time.plot(self.canvas)
            self.canvas.present()
            exp.clock.wait(1000)
            time_left -= 1
            #exp.clock.wait(self.show_instructions_for_seconds*1000)

    def plot_instructions(self, n, block_type, stimuli_type):
        instructions = ""
        if self.file != "" and self.folder != "":
            instructions = "../" + self.folder + "/" + self.file
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
