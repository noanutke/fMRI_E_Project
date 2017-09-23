#!/usr/bin/env python
# -*- coding: utf-8 -*-


from expyriment import control, stimuli, design, misc, io
from feedbackBar import FeedbackBar

design.defaults.experiment_background_colour = misc.constants.C_GREY
design.defaults.experiment_foreground_colour = misc.constants.C_BLACK

control.set_develop_mode(True)
digit_list = [1,1,1,2,5,3,5,5,7,8,9]
#design.randomize.shuffle_list(digit_list)

exp = control.initialize()


exp.data_variable_names = ["digit", "rt", "error"]

control.start(exp)
n=2
ISI = 1000
stimuliDuration = 1000
counter = 0

feedback_bar = FeedbackBar(10)
for digit in digit_list:
    canvas = stimuli.BlankScreen()
    target = stimuli.TextLine(text=str(digit), text_size=80)
    target.preload()
    target.plot(canvas)
    feedback_bar.paint_whole_line(canvas)
    canvas.present()
    key, rt = exp.keyboard.wait([misc.constants.K_RIGHT], stimuliDuration)
    if key is None:
        # we have waited stimuliDuration so we can remove
        canvas = stimuli.BlankScreen()
        feedback_bar.paint_whole_line(canvas)
        timeToClear = canvas.present()
        timeToUnload = target.unload()
        key, rt = exp.keyboard.wait([misc.constants.K_RIGHT], ISI - timeToUnload - timeToClear)
        if key:
            exp.clock.wait(ISI - rt) # wait the rest of the ISI before going on
            rt = rt + stimuliDuration
    else:
        exp.clock.wait(stimuliDuration - rt) # wait the rest of the stimuliDuration before removing
        # we have now waited stimuliDuration so we can remove
        canvas = stimuli.BlankScreen()
        feedback_bar.paint_whole_line(canvas)
        timeToClear = canvas.present()
        timeToUnload = target.unload()
        exp.clock.wait(ISI - timeToUnload - timeToClear)

    if counter > 1 and key == misc.constants.K_RIGHT and digit == digit_list[counter-n]:
        exp.data.add([digit, rt, "HIT"])
        feedback_bar.update_mark_position(30)
    elif counter > 1 and digit == digit_list[counter-n]:
        exp.data.add([digit, rt, "MISS"])
        feedback_bar.update_mark_position(-30)
    elif counter > 1 and key == misc.constants.K_RIGHT and digit != digit_list[counter-n]:
        exp.data.add([digit, rt, "FA"])
        feedback_bar.update_mark_position(-30)
    elif counter > 1 and key != misc.constants.K_RIGHT and digit != digit_list[counter-n]:
        exp.data.add([digit, rt, "CR"])
        feedback_bar.update_mark_position(30)

    counter += 1

control.end(goodbye_text="Thank you very much...", goodbye_delay=2000)
