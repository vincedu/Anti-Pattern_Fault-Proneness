#!/bin/bash

# passing the project list as an argument
filename=$1
folder_name=$2
project_name=$3

mkdir ../$folder_name

git clone $project_name


while read hash; do
    
     cd "./$folder_name"
     git checkout $hash
     cd ..
     echo "starting detection tests files"
     java -jar ./resources/TestFileDetector.jar "./$folder_name"
     
     echo "extract test files name from csv and writing it in a txt file"
     touch ./test_file.txt
     output=$(find . -type f -name "Output_Class_*.csv")
     
     number=$(wc -l < "$output")
     
     if [ $number -gt 1 ]
     then
     
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
       
       cp "./test.csv" "../$folder_name"
       rm "./test.csv"
    
    fi
    
    output=$(find . -type f -name "Output_*")
    
    for out in $output
    do 
       cp $out "../$folder_name"
    done 
    
    for out in $output
    do 
       rm $out "../$folder_name"
    done 
    
    cp "./Log.txt" "../$folder_name"
    rm "Log.txt"
     
    rm ./test_file.txt
  
done < $filename

rm -rf $folder_name
