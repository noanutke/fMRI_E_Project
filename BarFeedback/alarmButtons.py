
from expyriment import control, stimuli, io, design, misc
import random

perf1 = (255, 0 ,0)
perf5 = (0,255,0)
perf2 = (255, 128 ,0)
perf3 = (255, 255 ,0)
perf4 = (128, 255 ,0)

class AlarmButtons:

    def __init__(self, screen_height, screen_width, rt_average = 1000, show_alarms = False):

        if rt_average is None:
            self.rt_average = 1000
        else:
            self.rt_average = rt_average;
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.trial = 0

        self.show_alarms = show_alarms
        self.errors_in_row = 0
        self.success_in_row = 0
        self.perfArrayColors = [perf1,perf2,perf3,perf4,perf5]
        self.current_perf = 5;
        self.required_errors_in_row = 1;
        self.required_success_in_row = 1;
        self.chances_per_performace = [2,3,4,6,8]
        self.alarm_played = False;

    def get_alarm_played(self):
        temp = self.alarm_played;
        self.alarm_played = False;
        return temp;


    def get_color(self):
        return self.current_perf;

    def paint_alarm_buttons(self, canvas, is_error, rt = None):
        cross = stimuli.FixCross((50,50), (0,0), 5)
        cross.plot(canvas)
        if self.show_alarms == False:
            return

        is_slow = False;
        if rt is not None:
            if rt > self.rt_average:
                is_slow = True;

        if is_error == True or is_slow == True:
            self.errors_in_row += 1;
            self.success_in_row = 0;
            if self.errors_in_row == self.required_errors_in_row:
                self.errors_in_row = 0;
                if self.current_perf > 1:
                    self.current_perf -= 1;
        elif rt != None:
            self.errors_in_row = 0;
            self.success_in_row += 1;
            if self.success_in_row == self.required_success_in_row:
                self.success_in_row = 0;
                if self.current_perf < 5:
                    self.current_perf += 1;

        color = self.perfArrayColors[self.current_perf-1]
        size = (195,155)
        middleRect = stimuli.Rectangle(size, colour=color, position=(0,0))
        middleRect.plot(canvas)


    def should_play_alarm(self):
        randomNum = random.randint(1, self.chances_per_performace[self.current_perf-1])
        if randomNum == 1:
            self.alarm_played = True;
            return True;



