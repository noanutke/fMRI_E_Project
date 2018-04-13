from expyriment import control, stimuli, design, misc, io
import time as Time

class RestBlock:
    continue_key = misc.constants.K_SPACE
    exit_key = misc.constants.K_BACKSPACE
    show_instructions_for_seconds = 9
    show_cross_for_seconds = 1

    def __init__(self, task, lsl_stream, fixationTime, instructions_path,
                 exp=None, is_practice=False):
        self.task = task;
        self.show_cross_for_seconds = fixationTime;
        self.is_practice = is_practice
        self.canvas = stimuli.BlankScreen()
        self.exp = exp
        self.instructions_path = instructions_path
        self.file = file
        self.lsl_stream = lsl_stream
        self.task = task

    def start_rest(self):

        self.lsl_stream.push_sample(["instructions_start_1_task_" + self.task])
        cont = self.write_anticipation_text()

        self.lsl_stream.push_sample(["instructions_end_1_task_" + self.task])
        if cont == False:
            return False
        if self.is_practice:
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
        self.canvas = stimuli.BlankScreen()
        cross = stimuli.FixCross((50, 50), (0, 0), 5)
        cross.plot(self.canvas)
        self.canvas.present()
        key, rt = exp.keyboard.wait([self.exit_key], self.show_cross_for_seconds * 1000)
        if key is self.exit_key:
            return False
        return True


    def write_anticipation_text(self):
        self.canvas = stimuli.BlankScreen()

        self.plot_instructions()
        self.canvas.present()
        if self.is_practice:
            key, rt = self.exp.keyboard.wait([self.continue_key,\
                                              self.exit_key], self.show_instructions_for_seconds * 1000)
            if key is self.continue_key:
                return True
            elif key is self.exit_key:
                return False

        else:
            key, rt = self.exp.keyboard.wait([self.exit_key], self.show_instructions_for_seconds * 1000)
            if key is self.exit_key:
                return False
            return True


    def plot_instructions(self):
        instruction_picture = stimuli.Picture(self.instructions_path)
        instruction_picture.plot(self.canvas)
