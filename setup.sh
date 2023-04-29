#!/bin/bash

# If update command is passed, update the environment else create a new one
if [ "$1" = "update" ]; then
    mamba env update -f environment.yml -p ./.env
else
    if [ -d ./.env ]; then
        rm -rf .env
    fi
    mamba env create -f environment.yml -p ./.env
fi

# Load Libraries
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.env/lib

# Script to modify a line in file
#function modify_line {
    # $1: file path
    # $2: line number
    # $3: new line
    #sed -i "$2s/.*/$3/" $1
#}
#modify_line "$(pwd)/.env/lib/python3.7/site-packages/torch/utils/cpp_extension.py" 968 "                        '7.0', '7.2', '7.5', '8.6', '8.8']"

# command to modify file
sed -i "966s/.*/                        '7.0', '7.2', '7.5', '8.6', '8.8']/" .env/lib/python3.7/site-packages/torch/utils/cpp_extension.py