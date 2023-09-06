#!/bin/bash
python ./aws_batch_files/setup.py clean --all
python ./aws_batch_files/setup.py bdist_wheel
#python ./aws_batch_files/setup.py bdist_wheel pipes

