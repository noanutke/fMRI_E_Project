from expyriment import control, stimuli, design, misc, io
import pandas as pd


class RestBlock:
    show_instructions_for_seconds = 5
    show_cross_for_seconds = 1

    def __init__(self, next_block, exp):
        self.next_block = next_block
        self.canvas = stimuli.BlankScreen()

        self.paint_cross(exp)
        self.write_anticipation_text(next_block, exp)

    def paint_cross(self, exp):
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        cross.plot(self.canvas)
        self.canvas.present()
        exp.clock.wait(self.show_cross_for_seconds*1000)


    def write_anticipation_text(self, n, exp):
        time_left = self.show_instructions_for_seconds
        while time_left > 0:
            self.canvas = stimuli.BlankScreen()
            instructions = stimuli.Picture("C:/Users/NOA/fMRI_E_Project/Pictures/Slide" + n + ".png")
            instructions.plot(self.canvas)
            time = stimuli.TextBox(str(time_left), [200,200], [0,-250], None, 40)
            time.plot(self.canvas)
            self.canvas.present()
            exp.clock.wait(1000)
            time_left -= 1
            #exp.clock.wait(self.show_instructions_for_seconds*1000)
