from expyriment import control, stimuli, design, misc, io
import pandas as pd


class RestBlock:
    show_instructions_for_seconds = 3
    show_cross_for_seconds = 1

    def __init__(self, next_block, block_type, stimuli_type, exp):
        self.next_block = next_block
        self.canvas = stimuli.BlankScreen()

        self.paint_cross(exp)
        self.write_anticipation_text(next_block, block_type, stimuli_type, exp)

    def paint_cross(self, exp):
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        cross.plot(self.canvas)
        self.canvas.present()
        exp.clock.wait(self.show_cross_for_seconds*1000)


    def write_anticipation_text(self, n, block_type, stimuli_type, exp):
        time_left = self.show_instructions_for_seconds
        while time_left > 0:
            self.canvas = stimuli.BlankScreen()
            instructions = "C:/Users/NOA/fMRI_E_Project/Pictures/Slide" + n
            if block_type == 'p':
                instructions = instructions + "_" + block_type
                if stimuli_type != None:
                    instructions = instructions + "_" + stimuli_type
            instructions = instructions + ".png"

            instruction_picture = stimuli.Picture(instructions)
            instruction_picture.plot(self.canvas)
            time = stimuli.TextBox(str(time_left), [200,200], [0,-280], None, 40)
            time.plot(self.canvas)
            self.canvas.present()
            exp.clock.wait(1000)
            time_left -= 1
            #exp.clock.wait(self.show_instructions_for_seconds*1000)
