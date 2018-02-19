#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from runNbackTask import runNbackTask
from runStroopTask import runStroopTask
from expyriment import control, stimuli, design, misc, io
import datetime

screen_height = 600
screen_width = 800

runNbackTask(screen_height, screen_width)
runStroopTask(screen_height, screen_width)


