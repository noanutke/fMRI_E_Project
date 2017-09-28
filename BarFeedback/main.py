#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A line bisection task.

This example is appropriate to illustrates the use of the Android runtime environment for Exypriment on tablet PC.

"""
from __future__ import division
from nback import Nback
from restBlock import RestBlock

blocks = [(1,'a'), (3,'a'), (2, 'a'), (3, 'b'), (1, 'b'), (2, 'b')]
experiment = Nback(True)



for block in blocks:
    rest = RestBlock(str(block[0]), experiment.exp)
    n_back = experiment.run(block[0], block[1])

n_back.run_experiment()



from expyriment import control, stimuli, io, design, misc
import sched, time

