#!/bin/bash

# Determine the appropriate pip executable based on the operating system
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Error: This script cannot run on Windows using pyspark."
    exit 1
fi

# Create a virtual environment
python -m venv env_1

PIP_EXECUTABLE=env_1/bin/pip

$PIP_EXECUTABLE install -r requirements_docker.txt
#$PIP_EXECUTABLE install -r aws_batch_files/requirements.txt
$PIP_EXECUTABLE install pyspark
$PIP_EXECUTABLE install pyarrow

# Create a tarball of the virtual environment
tar -czvf dist/pyspark_venv.tar.gz env_1

# rm -rf env_1