#!/bin/bash

# passing the project list as an argument
filename=$1

# opening and reading the file
while IFS="," read -r url	stars	open_issues	commits_count	forks_count	last_commit_date	created_at	name	Group
do

   git clone $url
    
   echo "starting extracting commit log for $name project"
   python3 extract.py "$name"

   echo "removing the repository"
   rm -r $name

done < <(tail -n +2 $filename)
