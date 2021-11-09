""" This code is used to extract information from a git repository
    information are : commit log, list of all modified file, the complete version
    history of all identified test files and their production files.
    by Ossim Belias François Philippe"""

import pandas
from pydriller.git import Git
from pydriller.domain.commit import ModifiedFile, ModificationType
from pydriller.repository import Repository
import pandas as pd
import csv
from scipy import stats
from csv import reader
import numpy as np
import sys
import os
import pycurl
import time


def extractCommitLog(repository_name):
    """Extract the entire commit log of a repository"""
    gr = Git(repository_name)

    # writing the commit log in a csv
    f = open(repository_name + ".txt", "w")
    commits = gr.get_list_commits()
    for commit in commits:
        f.write(str(commit.hash) + "\n")


def extractModifiedFileList(repository_name):
    """Extract list of modified file for a repository"""
    for commit in Repository(repository_name).traverse_commits():
        for file in commit.modified_files:
            print("commit {}".format(commit.hash), "modified file {}".format(file.filename))


def extractMetric(folder):
    """Extract of the statistics for a repository"""
    name = folder[3:]
    f = open("./statistics_" + name + ".csv", "w")
    writer = csv.writer(f)
    writer.writerow(["number_test_files", "number_smells_detected"])

    x = []  # number of test files per commits
    y = []  # list of number of test smells per commits

    distribution = dict()

    # counting test file, production file and test smells file over the lifetime of the app
    for root, dirs, files in os.walk(folder):
        for filename in files:
            print(filename)

            if "Output_TestSmellDetection_" in filename:
                df = pd.read_csv(folder + "/" + filename)
                test_files = list(df["TestFilePath"])
                top = list(df.columns)
                with open(folder + "/" + filename, 'r') as read_obj:
                    csv_reader = reader(read_obj)
                    counter_test_smells = 0
                    for row in csv_reader:
                        for i in range(6, len(row)):
                            if row[i].lower() == "true":
                                counter_test_smells += 1
                                if top[i] in distribution:
                                    distribution[top[i]] += 1
                                else:
                                    distribution[top[i]] = 1
                            else:
                                if top[i] not in distribution:
                                    distribution[top[i]] = 0
                read_obj.close()
                x.append(len(test_files))
                y.append(counter_test_smells)
                writer.writerow([len(test_files), counter_test_smells])

    # print distribution
    smell_per_apps_file = open("./smells_per_apps_" + name + ".txt", "w")
    print("writing percentage of smells among the totality of smells detected for the app", name)
    smells_per_app = [(key, (val * 100) / sum(y)) for key, val in distribution.items()]
    smell_per_apps_file.write('\n'.join('{} {}'.format(x[0], x[1]) for x in smells_per_app))

    print("writing percentage of files affected by smells for the app", name)
    file_per_smell_file = open("./file_per_smells_" + name + ".txt", "w")
    files_per_smells = [(key, (val * 100) / sum(x)) for key, val in distribution.items()]
    file_per_smell_file.write('\n'.join('{} {}'.format(x[0], x[1]) for x in files_per_smells))

    # calcul of the co occurrence
    co_occurence_lst = []
    for index, t in enumerate(smells_per_app):
        smell_1 = t[0]
        percentage_1 = t[1]

        for j, s in enumerate(smells_per_app):
            smell_2 = s[0]
            percentage_2 = s[1]

            if smell_2 != smell_1:
                co_occurence_lst.append((smell_1, smell_2, (percentage_1 / 100) * (percentage_2 / 100) * 100))

    coocurence_file = open("./co_occurence_" + name + ".txt", "w")
    print("writing the co occurence matrix for app", name)
    coocurence_file.write('\n'.join('{} {} {}'.format(x[0], x[1], x[2]) for x in co_occurence_lst))


def extractProduction_Test_Files(filename):
    """Extract the complete version history of all identified test files and their production files."""

    df = pd.read_csv(filename)

    production_file = list(df["ProductionFilePath"].replace(np.nan, "nan"))
    test_file = list(df["TestFilePath"])
    app_name = list(df["App"])

    f = open('test.csv', "w")

    writer = csv.writer(f)

    for i in range(len(test_file)):
        if production_file[i] != "nan":
            print(production_file[i])
            writer.writerow([app_name[i], test_file[i], production_file[i]])


def spearman_test(x, y):
    """Calcul of the spearman test"""

    # mean of the smells inside
    if len(x) != 0:
        print("mean of smells detected accross the project", int(sum(y) / len(x)))
    else:
        print("mean of smells detected accross the project", 0)

    print(stats.spearmanr(x, y))


def main():
    print("starting")
    folder_name = sys.argv[1]
    extractMetric(folder_name)
    print("done")


if __name__ == "__main__":
    main()
