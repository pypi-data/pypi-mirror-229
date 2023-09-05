#!/bin/bash

# Create a virtual environment
python -m venv env_1

# Determine the appropriate pip executable based on the operating system
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PIP_EXECUTABLE=env_1/Scripts/pip
else
    PIP_EXECUTABLE=env_1/bin/pip
fi

$PIP_EXECUTABLE install -r requirements_docker.txt

# Create a tarball of the virtual environment
tar -czvf dist/pyspark_venv.tar.gz env_1