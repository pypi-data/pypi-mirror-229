#!/bin/bash

AWS_PROFILE="$1"

echo "AWS_PROFILE: $AWS_PROFILE"

# working airflow version 2.6.3
airflow db init
bash ./aws_batch_files/scripts/build.sh
# bash ./aws_batch_files/scripts/venv.sh

python ./aws_batch_files/services/uploader.py all $AWS_PROFILE
python ./aws_batch_files/dags/dag_service.py create $AWS_PROFILE
python ./aws_batch_files/dags/dag_service.py import $AWS_PROFILE
#python ./aws_batch_files/dags/dag_service.py instantiate $bucket_path