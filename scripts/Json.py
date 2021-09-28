"""This class handle all json file
   @author: Ossim Belias François Philippe
   @date: 28 september 2021"""

import gzip
import json
import csv


class Json:
    MAX_COUNT_FILE = 100

    # default headers of all csv
    headers = ["id",
               "full_name",
               "clone_url",
               "size",
               "stargazers_count",
               "watchers_count",
               "language",
               "has_issues",
               "has_projects",
               "has_downloads",
               "has_wiki",
               "has_pages",
               "forks_count",
               "mirror_url",
               "archived",
               "disabled",
               "open_issues_count",
               "forks",
               "open_issues",
               "watchers",
               "default_branch",
               "score"]

    # when the count > 100 add to the file errors values
    ERROR_VALUES = ["error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error",
                    "error"]

    def __init__(self, file_paths=[]):
        self.file_paths = file_paths
        self.json_files = list(dict())

    def extract_json(self):
        """Extract all json files"""
        for file in self.file_paths:
            f = open(file, 'r')
            file_content = f.read()
            self.json_files.append(json.loads(file_content))
            f.close()

    def convertToCsv(self, name):
        """convert json to csv"""
        directory = "./" + "combined_" + name + ".csv"

        output_file = open(directory, 'w')
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(self.headers)

        for json_file in self.json_files:
            if bool(json_file):  # check if the json is not empty before processing
                count = 0
                total_count = int(json_file['total_count'])
                if total_count >= 0:
                    items = json_file["items"]

                    for item in items:
                        values = self.extractValues(item)
                        csv_writer.writerow(values.values())
                        count += 1

                    if count > self.MAX_COUNT_FILE:
                        print("error for " + self.getFilename())
                        csv_writer.writerow(self.ERROR_VALUES)
        output_file.close()

    def getJsonFile(self):
        """:return all json files"""
        return self.json_files

    def getFilepaths(self):
        """:return all the file paths"""
        return self.file_paths

    def extractValues(self, item):
        """Extract the values of a row of the json file"""
        values = dict()
        for (key, value) in item.items():
            # Check if key is even then add pair to new dictionary
            if key in self.headers:
                values[key] = value
        return values

    def print_json(self):
        """Print all json files extracted"""
        print(self.json_files)

    def print_filepaths(self):
        """Print all file paths in a folder"""
        print(self.filename)
