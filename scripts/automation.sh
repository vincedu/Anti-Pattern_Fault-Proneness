#!/bin/bash

# passing the list of project as argument
project_list=$1

# opening and reading the file
while IFS="," read -r id name full_name url rest
do
  # cloning the repository
  git clone $url
  
  # detect tests files
  
  # match files with production files
  
  #run ts-dectect
  
  # removing the repository
  rm -r $name
  break
done < <(tail -n +2 $project_list)

