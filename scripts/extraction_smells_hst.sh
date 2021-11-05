#!/bin/bash

# passing the project list as an argument
project_name=$1
folder_name=$2

git clone $project_name

python3 extract.py "./$folder_name"
  

rm -rf $folder_name
