
from expyriment import control, stimuli, io, design, misc

class AlarmButtons:

    def __init__(self, screen_height, screen_width, alarms_order_list):
        self.button_rt = None
        self.button_accuracy = None
        self.text_rt = None
        self.text_accuracy = None
        self.alarms_order_list = alarms_order_list
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.add_rt_button()
        self.add_accuracy_button()
        self.buttons_status = []
        self.trial = 0
        self.alarm_on = False

        for status in alarms_order_list:
            self.buttons_status.insert(len(self.alarms_order_list), status)

    def add_rt_button(self, color = misc.constants.C_GREEN):
        self.button_rt = stimuli.Rectangle(size=(120, 80), \
                                           position=(0 - self.screen_width/2 + 100,\
                                                     0 + self.screen_height/2 - 60),\
                                           colour=color)
        self.text_rt = stimuli.TextLine(text="Slow", position=self.button_rt.position,
                                 text_colour=misc.constants.C_BLACK)


    def add_accuracy_button(self, color = misc.constants.C_GREEN):
        self.button_accuracy = stimuli.Rectangle(size=(120, 80), \
                                           position=(0 + self.screen_width/2 - 100,\
                                                     0 + self.screen_height/2 - 60),\
                                           colour=color)
        self.text_accuracy = stimuli.TextLine(text="Wrong", position=self.button_accuracy.position,
                                 text_colour=misc.constants.C_BLACK)


    def paint_alarm_buttons(self, canvas, is_error):
        color_accuracy = misc.constants.C_GREEN
        color_rt = misc.constants.C_GREEN

        if self.buttons_status[self.trial] == 1:
            self.alarm_on = True
            if is_error == True:
                color_accuracy = misc.constants.C_RED
            else:
                color_rt = misc.constants.C_RED
        else:
            self.alarm_on = False

        self.add_accuracy_button(color_accuracy)
        self.add_rt_button(color_rt)
        self.button_accuracy.plot(canvas)
        self.text_accuracy.plot(canvas)
        self.button_rt.plot(canvas)
        self.text_rt.plot(canvas)


    def is_alarm_on(self):
        return self.alarm_on

    def update_trial(self):
        self.trial += 1

