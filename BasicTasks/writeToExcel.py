from __future__ import division
from expyriment import control, stimuli, io, design, misc
import sched, time
import csv


class WriteToExcel:

    def __init__(self, file_name, type):
        self.stressHeaders = ["task", "subNumber", "time","order", "Stressful", "Unpleasant"]
        self.loadHeaders = ["task", "subNumber", "time","order", "Mental Demand", "Physical Demand", "Temporal Demand", "Performance",\
                       "Effort", "Frustration"]
        self.file_name = file_name + ".csv"
        self.file = open(self.file_name, 'w')
        self.writer = csv.writer(self.file)
        titles_row = []
        if type == "stress":
            titles_row = self.stressHeaders
        else:
            titles_row = self.loadHeaders

        if type == None:
            return
        else:
            self.writer.writerow(titles_row)

    def add_row(self, row):
        self.writer.writerow(row)

    def close_file(self):
        self.file.close()

    def open_file(self):
        self.file = open(self.file_name)
        self.writer = csv.writer(self.file)


