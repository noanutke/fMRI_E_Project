#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

from expyriment import control, stimuli, io, design, misc
import sched, time


class Grid:
    positions_locations = {"TopLeft": (-200,150), "TopMiddle": (0, 150), "TopRight": (200, 150), \
                        "Left": (-200, 0), "Right": (200, 0), \
                        "BottomLeft": (-200, -150), "BottomMiddle": (0, -150), "BottomRight": (200, -150)}

    positions_indices = ["TopLeft", "TopMiddle", "TopLeft", "Left", "Right", "BottomLeft", "Right", "BottomRight"]


    positions_indices2 = {"1": "TopLeft", "2": "TopMiddle", "3": "TopRight", "4": "Left", "5": "Right", \
                         "6": "BottomLeft", "7": "BottomMiddle", "8": "BottomRight"}

    def __init__(self, should_paint_grid):
        self.should_paint_grid = should_paint_grid

    def paint_grid(self, canvas):
        if self.should_paint_grid == 0:
            return 0;
        line_horsizontal1 = stimuli.Line((-300, 80), (300, 80), 5)
        line_horsizontal2 = stimuli.Line((-300, -80), (300, -80), 5)
        line_vertical1 = stimuli.Line((-100, 200), (-100, -200), 5)
        line_vertical2 = stimuli.Line((100, 200), (100, -200), 5)
        time_delay = 0;
        time_delay += line_horsizontal1.preload()
        time_delay += line_horsizontal2.preload()
        time_delay += line_vertical1.preload()
        time_delay += line_vertical2.preload()
        time_delay += line_vertical1.plot(canvas)
        time_delay += line_vertical2.plot(canvas)
        time_delay += line_horsizontal1.plot(canvas)
        time_delay += line_horsizontal2.plot(canvas)
        return time_delay;