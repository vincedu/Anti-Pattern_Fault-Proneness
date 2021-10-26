#!/bin/bash

# passing the project list as an argument
filename=$1

# opening and reading the file
while IFS="," read -r id name full_name url remaing
do

   git clone $url
    
   echo "starting detection tests files"
   java -jar ./resources/TestFileDetector.jar "./$name"

   echo "extract test files name from csv and writing it in a txt file"
   touch ./test_file.txt
   output=$(find . -type f -name "Output_Class_*.csv")
   while IFS="," read -r app tag Filepath relativeFilePath remaing
   do 
      echo  "$Filepath" > ./test_file.txt
   
   done < "$output"
   
   echo "matching files with production files"
   java -jar ./resources/TestFileMapping.jar "./test_file.txt"

   echo "running detection smells"
   
   output=$(find . -type f -name "Output_TestFileMappingDetection_*.csv")
   python3 extract.py "$output"


   java -jar ./resources/TestSmellDetector.jar "./test.csv"

   echo "removing the repository"
   rm ./test_file.txt
   rm -r $name
   break

done < <(tail -n +2 $filename)