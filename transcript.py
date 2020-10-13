# This merges the transcripts from YouTube videos based on timestamp
# It was build to merge the transcripts of players on Chess24 live Banter Blitz tournament

import re
from operator import itemgetter
import csv
import logging

log = logging.getLogger("merge transcript")
logging.basicConfig(level=logging.INFO)


def adjust_time(time, offset):
    if offset == 0:
        return time
    else:
        time_list = time.split(":")
        minutes = int(time_list[0])
        seconds = int(time_list[1])
        seconds += offset
        if seconds > 60:
            seconds = seconds - 60
            minutes += 1

    return "{:02d}".format(minutes) + ":" + "{:02d}".format(seconds)


class FileInfo:
    def __init__(self, file, label, time):
        self.file = file
        self.label = label
        self.adjust_time = time


class Comment:

    def __init__(self, time_stamp, label):
        self.time_stamp = time_stamp
        self.label = label
        self.comment_list = []
        self.time_value = int(time_stamp.replace(":", ""))

    def to_string(self):
        return self.time_stamp + " " + self.label + "  comments=" + str(
            len(self.comment_list)) + self.get_comments()

    def get_comments(self):
        return '|'.join(self.comment_list)


def get_commentary_from_file_into_list(file_name):
    line_list = [line.rstrip('\n') for line in open(file_name)]
    return line_list


def is_time_stamp(text):
    time_pattern = re.compile("\d{2}:\d{2}")
    return time_pattern.match(text.strip()) and len(text.strip()) == 5


def extract_comments(file_info):
    file_name = file_info.file
    line_list = get_commentary_from_file_into_list(file_name)

    commentary_list = []

    current_time = None
    for l in line_list:
        if is_time_stamp(l.strip()):
            if current_time is not None:
                commentary_list.append(current_time)
            time = adjust_time(l.strip(), file_info.adjust_time)
            current_time = Comment(time, file_info.label)
        else:
            if current_time is not None:
                current_time.comment_list.append(l.strip())
    return commentary_list


def process_file(file_info):
    reformatted_comments = extract_comments(file_info)
    return reformatted_comments


def print_data(data):
    print(len(data))
    for comment in data:
        print(comment.time_value, comment.time_stamp, comment.label, comment.get_comments())


def combine_data_to_list(data1, data2):
    combined = []
    for comment in data1:
        row = [comment.time_value, comment.time_stamp, comment.label, comment.get_comments()]
        combined.append(row)
    for comment in data2:
        row = [comment.time_value, comment.time_stamp, comment.label, comment.get_comments()]
        combined.append(row)

    return combined


def export_merged_data(data, filename):
    # data is a list of lists
    with open("merged_" + filename + ".csv", mode='w', newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["id", "time", "label", "comment"])
        for line in data:
            log.info(line)
            writer.writerow(line)


def merge_transcript(file1, file2, file1_label, file2_label, time_offset1, time_offset2):
    # file  = file_name e.g "carlsen.csv"
    # label = a name for the data in the file "carlsen"
    # time_offset = this is value is used to sync the two transcripts so comments made at the same appear together.

    file1_data = process_file(FileInfo(file1, file1_label, time_offset1))
    file2_data = process_file(FileInfo(file2, file2_label, time_offset2))
    combined = combine_data_to_list(file1_data, file2_data)

    inter = sorted(combined, key=itemgetter(0), reverse=False)
    # sorted_lst = sorted(inter, key=itemgetter(2))

    export_merged_data(inter, file1_label + "_" + file2_label)
