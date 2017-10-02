from __future__ import division
import pygame
from expyriment import control, stimuli, io, design, misc
import sched, time
import csv


class WriteToExcel:

    def __init__(self, file_name, titles_row):
        self.file = open(file_name + ".csv", 'w')
        self.writer = csv.writer(self.file)
        self.writer.writerow(titles_row)

    def add_row(self, row):
        self.writer.writerow(row)

    def close_file(self):
        self.file.close()


