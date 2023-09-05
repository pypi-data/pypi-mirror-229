
# STEP 1: Libraries needed
import json

from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import (
    EmrCreateJobFlowOperator,
    EmrTerminateJobFlowOperator,
    EmrAddStepsOperator
)
from airflow.providers.amazon.aws.sensors.emr import (
    EmrJobFlowSensor,
    EmrStepSensor
)
# from airflow.providers.amazon.aws.transfers.s3_to_local import S3ToLocalOperator
# from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime, timezone

region = "us-east1"
zone = region + '-b'
stage_config = '{"environment": "gaia-airflow-test", "log_level": "warning", "bucket_name": "gaia-aws-airflow-try", "project_id": "google-project-id", "region": "us-east1", "template_id": "test-template", "project_name": "test", "target": "wf_dev", "unique_iteration_id": "", "unique_template_id": "", "specific_jobs_to_run": [], "force_remove_all_prerequisites": false, "cluster_duration_sec": 3600, "cluster_conf": {"Name": "test-cluster", "ReleaseLabel": "emr-6.12.0", "Applications": [{"Name": "Spark"}], "Configurations": [{"Classification": "spark-env", "Configurations": [{"Classification": "export", "Properties": {"PYSPARK_PYTHON": "/usr/bin/python3.9"}}]}], "Instances": {"InstanceGroups": [{"Name": "Primary node", "Market": "SPOT", "InstanceRole": "MASTER", "InstanceType": "m1.medium", "InstanceCount": 1}], "KeepJobFlowAliveWhenNoSteps": true, "TerminationProtected": false}, "JobFlowRole": "EMR_EC2_DefaultRole", "ServiceRole": "EMR_DefaultRole", "LogUri": "s3://gaia-aws-airflow-try/logs/emr/", "BootstrapActions": [{"Name": "init_actions", "ScriptBootstrapAction": {"Args": [], "Path": "s3://gaia-aws-airflow-try/testAROA2RVWNELOGORL4LZUO_ori/main/aws_batch_files/scripts/cluster-init-actions.sh"}}]}, "spark_properties": [["spark.pyspark.python", "python3"], ["spark:spark.sql.execution.arrow.maxRecordsPerBatch", "10"], ["spark:spark.driver.memory", "48"], ["spark:spark.executor.memory", "8"], ["spark:spark.executor.memoryOverhead", "8"], ["spark:spark.sql.shuffle.partitions", "2000"], ["spark.sql.parquet.columnarReaderBatchSize", "1024"], ["spark.hadoop.fs.gs.implicit.dir.repair.enable", "false"]], "extra_job_params": {"MODE": "MANUAL"}}'
project_id = "google-project-id"
template_id = "test-template"
bucket_name = "gaia-aws-airflow-try"
bucket_path = "s3://gaia-aws-airflow-try/testAROA2RVWNELOGORL4LZUO_ori/main"
project_name = "test"
whl_file_name = "test-0.0.0.tar.gz"
target = "wf_dev"
orig_project_name = project_name
unique_template_id = ""
cluster_config = '{"Name": "test-cluster", "ReleaseLabel": "emr-6.12.0", "Applications": [{"Name": "Spark"}], "Configurations": [{"Classification": "spark-env", "Configurations": [{"Classification": "export", "Properties": {"PYSPARK_PYTHON": "/usr/bin/python3.9"}}]}], "Instances": {"InstanceGroups": [{"Name": "Primary node", "Market": "SPOT", "InstanceRole": "MASTER", "InstanceType": "m1.medium", "InstanceCount": 1}], "KeepJobFlowAliveWhenNoSteps": true, "TerminationProtected": false}, "JobFlowRole": "EMR_EC2_DefaultRole", "ServiceRole": "EMR_DefaultRole", "LogUri": "s3://gaia-aws-airflow-try/logs/emr/", "BootstrapActions": [{"Name": "init_actions", "ScriptBootstrapAction": {"Args": [], "Path": "s3://gaia-aws-airflow-try/testAROA2RVWNELOGORL4LZUO_ori/main/aws_batch_files/scripts/cluster-init-actions.sh"}}]}'
job_flow_override = json.loads(cluster_config)
if unique_template_id:
    template_id = template_id + '_' + unique_template_id
    orig_project_name = orig_project_name + '_' + unique_template_id

extra_dag_job_params = json.dumps({"MODE": "AIRFLOW", "TEST_EXEC_DATE": "{{ next_execution_date }}"})

now = datetime.now().replace(tzinfo=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
dag_start_date = now - timedelta(days=1)

# STEP 3: Set default arguments for the DAG
default_dag_args = {
    # 'start_date': dag_start_date,
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with DAG(
    dag_id=orig_project_name + '_' + target + '_dag',
    default_args=default_dag_args,
    schedule_interval=None,  # Set to None to prevent automatic scheduling
    is_paused_upon_creation=False,  # Start the DAG in a paused state
    # schedule_interval=timedelta(days=1),
    tags=[orig_project_name + '_' + target + '_dag'],
) as dag:

    # # [START howto_operator_emr_manual_steps_tasks]
    cluster_creator = EmrCreateJobFlowOperator(
        task_id="create_cluster",
        job_flow_overrides=job_flow_override,
        aws_conn_id="aws_default",
        emr_conn_id='emr_default',
    )

    step_get_data = EmrAddStepsOperator(
        task_id='step_get_data',
        job_flow_id=cluster_creator.output,
        aws_conn_id='aws_default',
        steps=[{
            "Name": "Run Spark Job",
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": [
                    "spark-submit", 
                    "--deploy-mode", "client",
                    "--master", "yarn",
                    # "--archives",bucket_path + "/dist/pyspark_venv.tar.gz#venv"
                    "--py-files", bucket_path + "/dist/" + whl_file_name,
                    bucket_path + "/aws_batch_files/stages/get_data/main.py",
                    stage_config, "{{params.start_date}}", "end_time","params"
                ]
            }
        }],
        params={
            # "BUCKET_NAME": BUCKET_NAME,
            # "s3_script": s3_script,
            "start_date": "{execution_date}",
        },
    )

    step_checker = EmrStepSensor(
        task_id='watch_step',
        # job_flow_id="{{ task_instance.xcom_pull('create_cluster', key='return_value') }}",
        job_flow_id=cluster_creator.output,
        step_id="{{ task_instance.xcom_pull(task_ids='step_get_data', key='return_value')[0] }}",
        aws_conn_id='aws_default',
    )

    # cluster_remover = EmrTerminateJobFlowOperator(
    #     task_id='remove_cluster',
    #     # job_flow_id="{{ task_instance.xcom_pull('create_cluster', key='return_value') }}",
    #     job_flow_id=cluster_creator.output,
    #     aws_conn_id='aws_default',
    # )

    step_get_data >> step_checker
