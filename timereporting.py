#!/usr/bin/env python3
"""
Example: python3 timereporting.py --csv ./Arbetstidsrapport.csv -p 19RExxxx -o syntronic.csv
"""

import argparse
import csv
import re


TASK = 2


class Time(object):
    def __init__(self, timestring: str):
        "docstring"
        hour, minute = timestring.split(":")
        self.hour = int(hour)
        self.minute = int(minute)

    @property
    def minute_deimal(self) -> float:
        return self.minute / 60

    def __add__(self, other: "Time"):
        total_minutes = self.minute + other.minute
        hour = self.hour + other.hour + total_minutes // 60
        minuites = total_minutes % 60
        return Time(f"{hour}:{minuites}")

    def __sub__(self, other):
        minuites = self.minute - other.minute
        if minuites >= 0:
            hour = self.hour - other.hour
        else:
            hour = self.hour - other.hour - 1
            if hour < 0:
                raise ValueError("Does not handle negative hours!")

            minuites = 60 + minuites

        return Time(f"{hour}:{minuites}")

    def __repr__(self) -> str:
        return f"{self.hour}:{self.minute}"


def sum_time(timestamps):
    time_worked = []
    for i in range(0, len(timestamps), 2):
        in_time = Time(timestamps[i])
        out_time = Time(timestamps[i + 1])
        time_worked.append(out_time - in_time)
    acc = Time("0:0")
    for time in time_worked:
        acc += time

    print(acc.hour + acc.minute_deimal)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="time_report.csv")
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-c", "--csv", required=True)
    requiredNamed.add_argument("-p", "--projectnum", required=True)
    args = parser.parse_args()
    timestamps = []
    dates = []
    with open(args.csv, "r") as csvfile:
        reader = csv.reader([line.replace("\0", "") for line in csvfile], delimiter=";")
        reader.__next__()
        for row in reader:
            if not row:
                continue
            new_timestamps = re.findall(r"[0-9][0-9]:[0-9][0-9]", row[2])
            timestamps += new_timestamps
            for _ in range(len(new_timestamps) // 2):
                dates.append(row[0])
    with open(args.output, "w", newline="") as outputfile:
        writer = csv.writer(outputfile, delimiter=";")
        writer.writerow(["Time In", "TimeOut", "Project Number", "Task ID", "Remark"])
        for date, i in zip(dates, range(0, len(timestamps), 2)):
            in_time = timestamps[i]
            out_time = timestamps[i + 1]
            writer.writerow(
                [f"{date} {in_time}", f"{date} {out_time}", args.projectnum, TASK, ""]
            )
    sum_time(timestamps)
