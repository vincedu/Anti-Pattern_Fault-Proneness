""" This code is used to extract information from a git repository
    information are : commit log, list of all modified file, the complete version
    history of all identified test files and their production files.
    by Ossim Belias François Philippe"""

from pydriller.git import Git
from pydriller.domain.commit import ModifiedFile, ModificationType
from pydriller.repository import Repository
import pandas as pd
import csv
import numpy as np


def extractCommitLog(repository_name):
    """Extract the entire commit log of a repository"""
    gr = Git(repository_name)
    commits = gr.get_list_commits()
    # TODO once you have the list of projects put information in a csv
    for commit in commits:
        print("commit {}".format(commit.hash),
              "Author: {}".format(commit.author),
              "Date: {}".format(commit.author_date),
              "Message: {}".format(commit.msg))


def extractModifiedFileList(repository_name):
    """Extract list of modified file for a repository"""
    # TODO once you have the list of projects put information in a csv
    for commit in Repository(repository_name).traverse_commits():
        for file in commit.modified_files:
            print("commit {}".format(commit.hash), "modified file {}".format(file.filename))


def extractCompleteHistory():
    """Extract the complete version history of all identified test files and their production files."""
    return ""

def extractProduction_Test_Files():
    """Extract the complete version history of all identified test files and their production files."""
    filename1 = "./production_test_files.csv"

    df = pd.read_csv(filename1)

    production_file = list(df["ProductionFilePath"].replace(np.nan, "nan"))
    test_file = list(df["TestFilePath"])

    f = open('test.csv', "w")

    writer = csv.writer(f)

    for i in range(len(test_file)):
        if production_file[i] != "nan":
            print(production_file[i])
            writer.writerow([test_file[i], production_file[i]])
    

def main():
    # list of all projects
    filename = "./combined_projects.csv"

    df = pd.read_csv(filename)
    repositories_list = list(df["name"])

    for repo in repositories_list:
        extractCommitLog(repo)
        extractModifiedFileList(repo)
        break

    print("Done")


if __name__ == "__main__":
    main()
