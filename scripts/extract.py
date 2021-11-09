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
    # TODO once you have the list of projects put information in a csv
    for commit in commits:
        f.write(str(commit.hash) + "\n")

        """print("commit {}".format(commit.hash),
              "Author: {}".format(commit.author),
              "Date: {}".format(commit.author_date),
              "Message: {}".format(commit.msg))"""


def extractModifiedFileList(repository_name):
    """Extract list of modified file for a repository"""
    # TODO once you have the list of projects put information in a csv
    for commit in Repository(repository_name).traverse_commits():
        for file in commit.modified_files:
            print("commit {}".format(commit.hash), "modified file {}".format(file.filename))


def extractMetric(folder):
    name = folder[3:]
    f = open("./statistics_" + name + ".csv", "w")
    writer = csv.writer(f)
    writer.writerow(["number_test_files", "number_smells_detected"])

    # a list to count distinct test file
    test_files = []

    x = []
    y = []

    distribution = []
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
                    counter_testSmells = 0
                    for row in csv_reader:
                        for i in range(6, len(row)):
                            if row[i].lower() == "true":
                                counter_testSmells += 1
                                if top[i] in distribution:
                                    distribution[top[i]] += 1
                                else:
                                    distribution[top[i]] = 1
                            else:
                                if top[i] not in distribution:
                                    distribution[top[i]] = 0
                read_obj.close()
                x.append(len(test_files))
                y.append(counter_testSmells)
                writer.writerow([len(test_files), counter_testSmells])

    # print distirbution
    smell_per_apps_file = open("./smells_per_apps_" + name + ".txt", "w")
    print("writing percentage of smells among the totality of smells detected for the app", name)
    smells_per_app = [(key, (val * 100) / sum(y)) for key, val in distribution.items()]
    smell_per_apps_file.write('\n'.join('{} {}'.format(x[0], x[1]) for x in smells_per_app))

    print("writing percentage of files affected by smells for the app", name)
    file_per_smell_file = open("./file_per_smells_" + name + ".txt", "w")
    files_per_smells = [(key, (val * 100) / sum(x)) for key, val in distribution.items()]
    file_per_smell_file.write('\n'.join('{} {}'.format(x[0], x[1]) for x in files_per_smells))

    # calcul of the co occurence
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

    # spearmane test
    # print("performing spearman test")

    # try:
    # df = pd.read_csv("./statistics_" + name + ".csv")
    # print(df)
    # spearman_test(x,y)
    # except pd.errors.EmptyDataError as e:
    # print(e)


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


def extract_metrics_2(repository_name):
    gr = Git(repository_name)
    commits = gr.get_list_commits()

    # list to count distint java file and a list to count distinct test file
    java_files = []
    test_files = []

    for commit in commits:
        gr.checkout(str(commit.hash))
        print("checking out to", commit.hash)
        for root, dirs, files in os.walk(repository_name):
            for file in files:
                if file.endswith(".java"):
                    if "test" in file.lower() and file not in test_files:
                        test_files.append(file)
                    elif file not in java_files:
                        java_files.append(file)

    print(len(java_files), len(test_files))


def spearman_test(x, y):
    # x = list(df["number_test_files"])
    # y = list(df["number_smells_detected"])

    # mean of the smells inside
    if len(x) != 0:
        print("mean of smells detected accross the project", int(sum(y) / len(x)))
    else:
        print("mean of smells detected accross the project", 0)

    print(stats.spearmanr(x, y))


def download():
    url = "https://api.github.com/search/repositories?q=language:java+topic:java+is:public+fork:false+stars:>=1000" \
          "+archived:false+pushed:>=2020-01-01" \
          "&per_page=100&page=1"

    file = open('./pycurl_' + str(1) + '.json', 'wb')
    crl = pycurl.Curl()
    crl.setopt(crl.URL, url)
    crl.setopt(crl.WRITEDATA, file)
    crl.perform()
    crl.close()

    print("finished downloading projects for page " + str(1))


def main():
    folder_name = sys.argv[1]
    extractProduction_Test_Files(folder_name)
    # list of all projects
    # filename = "./data.csv"

    # df = pd.read_csv(filename)
    # repositories_list = list(df["name"])

    # for repo in repositories_list:
    # repo_name = sys.argv[1]
    
    # dirs = os.listdir("./java_data")
    # for dir in dirs:
    # print(dir)
    # extractCommitLog("./java_data/"+ dir)
     
    
    # extractCommitLog(repo_name)

    # extractModifiedFileList(repo)
    # break

    # print("Done")
    # print("starting")
    # folder_name = sys.argv[1]
    # extractMetric(folder_name)
    # download()
    # print("done")


if __name__ == "__main__":
    main()
