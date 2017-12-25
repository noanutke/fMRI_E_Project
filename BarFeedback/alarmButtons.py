
from expyriment import control, stimuli, io, design, misc
import random

red = (255, 0 ,0)
green = (0,255,0)


class AlarmButtons:

    def __init__(self, screen_height, screen_width, colors_list, alarms_list,\
                 lsl_outlet, show_alarms = False):

        self.lsl_outlet = lsl_outlet
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.trial = 0

        self.colors_list = colors_list
        self.alarms_list = alarms_list

        self.show_alarms = show_alarms
        self.from_string_to_color = {"green": green, "red": red}

    def paint_alarm_buttons(self, canvas, should_incriment_trial = True):
        time_delay = 0
        cross = stimuli.FixCross((50,50), (0,0), 5)
        time_delay += cross.plot(canvas)
        if self.show_alarms == False:
            return 0;

        color = green

        if should_incriment_trial == True:
            self.trial += 1
        if self.trial != 0:
            self.lsl_outlet.push_sample(["color_" + self.colors_list[self.trial-1]])
            color = self.from_string_to_color[self.colors_list[self.trial-1]]
        size = (195,155)
        middleRect = stimuli.Rectangle(size, colour=color, position=(0,0))
        time_delay += middleRect.plot(canvas)


        return time_delay


    def should_play_alarm(self):
        if self.show_alarms == False:
            return False
        if self.alarms_list[self.trial-1] == "alarm":
            return True
        else:
            return False



