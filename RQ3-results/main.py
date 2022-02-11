"""" code for RQ3 paper
     code by: Ossim Belias
"""

import os
import json
import argparse
from dataclasses import dataclass
from pydriller.git import Git
import subprocess
import csv
import pandas as pd

from pydriller.repository import Repository

""" structures declaration """


@dataclass
class Project:
    name: str
    url: str
    tags: list


@dataclass
class Params:
    name: str
    detection_pydriller: list
    detection_openSzz: list
    detection_combination: list
    detection_manual: list


""" end of structures declaration"""

""" Helper functions declaration """


def calculate_intersection(list1, list2):
    """return the instersection between the two lists"""
    return list(set(list1) & set(list2))


def write_row_in_csv(filename, row, header=[]):
    """write a row in the specified csv file"""
    f = open(filename, "a")
    writer = csv.writer(f)
    if len(header) > 0:
        # write the header
        writer.writerow(header)

    # write the data
    writer.writerow(row)
    f.close()


""" End of helper functions declaration"""


def pydriller_detection(project: Project):
    """ return the list of file containing bugs"""

    # cloning the repository
    clone_project = ["git", "clone", project.url]
    p1 = subprocess.Popen(clone_project)
    p1.wait()

    print("name", project.name)

    # some projects names don't correspond to the github name
    if "systemml" in project.name:
        project.name = "systemds"
    elif "wss4j" in project.name:
        project.name = "ws-wss4j"

    gr = Git(project.name)
    files_detected = []

    commits = gr.get_list_commits()
    for commit in commits:
        _list = gr.get_commits_last_modified_lines(commit)
        files_detected += [file for file in _list if file not in files_detected and file.endswith(".java")]

    # deleting the repo to save disk space
    delete_project = ["rm", "-rf", project.name]
    p2 = subprocess.Popen(delete_project)
    p2.wait()

    return files_detected


def detection(name, directory):
    """ return the list of file containing bug using the given directory"""
    files_detected = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if name in file and file.endswith(".json"):
                f = open(directory + file, 'r')
                file_content = f.read()
                data = json.loads(file_content)
                for d in data:
                    if len(d["bug_fixes"]) > 0 and d["file"] not in files_detected:
                        files_detected.append(d["file"])

    return files_detected


def voting_system(py_dectect, open_detect):
    """ return the list of common elements between the two list"""
    return calculate_intersection(py_dectect, open_detect)


def compare_with_ground_truth(params: Params):
    """ return in a list:
         - the percentage of detection for the two tools
         - the percentage of detection for pydriller tool
         - the percentage of detection for openszz tool
         - the name of the current project
    """
    percent_pydriller = len(calculate_intersection(params.detection_manual, params.detection_pydriller)) / len(
        params.detection_manual) if len(params.detection_manual) != 0 else 0.0

    percent_openszz = len(calculate_intersection(params.detection_manual, params.detection_openSzz)) / len(
        params.detection_manual) if len(params.detection_manual) != 0 else 0.0

    percent_combination = len(calculate_intersection(params.detection_manual, params.detection_combination)) / len(
        params.detection_manual) if len(params.detection_manual) != 0 else 0.0

    return [str(percent_combination), str(percent_pydriller), str(percent_openszz), params.name]


def process(project: Project):
    """ this function handle:
       - the manual detection
       - openszz detection
       - pydriller dectection
       - the voting system
       - the writing of the percentage in the csv file
    """
    print("manual detection", project.name)
    manual_detection = detection(project.name, "./release-level-data/")

    print("openszz detection", project.name)
    openszz_detection = detection(project.name, "./release-level-data-OpenSZZ/")

    print("pydriller detection", project.name)
    pydril_detection = pydriller_detection(project)

    print("voting system", project.name)
    vote_res = voting_system(py_dectect=pydril_detection, open_detect=openszz_detection)

    params = Params(name=project.name,
                    detection_pydriller=pydril_detection,
                    detection_openSzz=openszz_detection,
                    detection_combination=vote_res,
                    detection_manual=manual_detection)

    print("percentage production", params.name)
    percentage = compare_with_ground_truth(params)

    print("writing", percentage)
    write_row_in_csv(filename="./total.csv", row=percentage)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=' parser')
    parser.add_argument("--file",
                        type=str,
                        nargs='?',
                        dest='file',
                        help="csv file")

    args = parser.parse_args()
    filename = args.file

    df = pd.read_csv(filename)

    for i, row in df.iterrows():
        tags = row.releases_tags.split(",")
        tags = [t.strip() for t in tags]

        # construction of project params
        project = Project(name=row.project, url=row.url, tags=tags)
        process(project)
