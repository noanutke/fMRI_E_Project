#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from nback import Nback


n_back = Nback(True, 2, 'a')
n_back.run_experiment()



from expyriment import control, stimuli, io, design, misc
import sched, time

