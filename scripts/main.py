""" This code create a list of all github project"""

from Json import Json
import pandas as pd
import os
import sys


def write_to_file(my_dict, filename):
    outF = open(filename, "w")
    for key, value in my_dict.items():
        value.sort()
        test_list = value
        value = [i for n, i in enumerate(test_list) if i not in test_list[:n]]
        outF.write("forks:" + str(key) + ": ")
        outF.write("[")
        for i in range(len(value)):
            if i != len(value) - 1:
                outF.write(str(value[i]) + ", ")
            else:
                outF.write(str(value[i]))
        outF.write("]")
        outF.write("\n")
    outF.close()


def main():
    # csv creation
    directory = "./data"

    file_paths = []
    for filename in os.listdir(directory):
       file_paths.append(directory + "/" + filename)

    filePath = sys.argv[1]
    json_files = Json(file_paths)
    json_files.extract_json()
    json_files.convertToCsv(filePath)

    print("Done for the csv creation")



if __name__ == "__main__":
    main()
