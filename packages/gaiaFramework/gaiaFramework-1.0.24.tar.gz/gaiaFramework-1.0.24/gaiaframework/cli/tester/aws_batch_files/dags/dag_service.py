import os
import boto3
import sys
import requests
from json import load as json_load
from json import dumps as json_dumps
from textwrap import dedent


# from airflow.providers.amazon.aws.example_dags.example_emr_job_flow_manual_steps import EmrCreateJobFlowOperator


class Dag():
    def __init__(self, AWS_PROFILE, dag_config_params=None):
        if AWS_PROFILE:
            boto3.setup_default_session(profile_name=AWS_PROFILE)
        self.storage_client = boto3.resource('s3')

        file_path = sys.modules[self.__class__.__module__].__file__
        self.curr_path = file_path[:file_path.rfind("aws_batch_files")]

        with open(self.curr_path + '/aws_batch_files/batch_config.json') as batch_cfg_file:
            self.config = json_load(batch_cfg_file)

        stage_config = self.config
        self.user_id = ''
        env_type = os.environ.get('SPRING_PROFILES_ACTIVE')
        if (not env_type == 'production') and (not env_type == 'staging'):
            command = 'gcloud config get-value account'
            self.user_id = boto3.client('sts').get_caller_identity().get('UserId').replace(':', '_')
            stage_config['user_id'] = self.user_id

        self.environment = stage_config['environment']
        self.bucket_name = stage_config['bucket_name']
        self.project_id = stage_config['project_id']
        self.project_name = stage_config['project_name']
        self.target = stage_config['target']
        self.unique_template_id = stage_config['unique_template_id']
        self.region = stage_config['region']
        self.zone = self.region + '-b'  # TODO: Check if we can configure this as well
        self.template_id = stage_config['template_id']
        self.unique_iteration_id = stage_config['unique_iteration_id']
        self.spark_properties = self.flatten(stage_config['spark_properties'])
        self.cluster_conf = stage_config['cluster_conf']
        self.cluster_id = self.get_cluster_id(self.cluster_conf['Name'])
        # self.cluster_name = stage_config['cluster_conf']['managed_cluster']['cluster_name']
        # self.cluster_duration = stage_config['cluster_duration_sec']
        # self.managed_cluster = stage_config['cluster_conf']['managed_cluster']
        if self.unique_iteration_id:
            self.folder_path = self.project_name + self.user_id + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + self.user_id + '/main'

        self.bucket_path = f's3://{self.bucket_name}/{self.folder_path}'
        self.project_path = 'projects/{project_id}/regions/{region}'.format(project_id=self.project_id,
                                                                            region=self.region)

        if self.target:
            self.file_name = self.project_name + "_" + self.target + "_dag.py"
        else:
            self.file_name = self.project_name + "_dag.py"

        self.file_path = self.curr_path + self.file_name

        # This setting will give the dag an execution date of the day before its creation.
        self.dag_start_delay = 1
        self.start_as_paused = True
        self.use_cluster_bootstrap = self.config['use_cluster_bootstrap']
        init_actions_path = f'{self.bucket_path}/aws_batch_files/scripts/cluster-init-actions.sh'
        if not type(self.cluster_conf['BootstrapActions']) == list:
            self.cluster_conf['BootstrapActions'] = []
        if self.use_cluster_bootstrap:
            self.cluster_conf['BootstrapActions'].append(
                {
                    "Name": "init_actions",
                    "ScriptBootstrapAction": {
                        "Args": [],
                        "Path": init_actions_path
                    }
                }
            )

    def flatten(self, l):
        return [item.strip() for sublist in l for item in sublist]

    def get_new_cluster_dag_code(self) -> str:
        """! Get basic code for dag creation
        Returns:
            A string, containing tailored code for creation of a DAG
        """
        dag_str = '''
        ''' + self.get_dag_conf() + '''
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

            ''' + self.get_stages_str('cluster_creator.output') + '''

            # cluster_remover = EmrTerminateJobFlowOperator(
            #     task_id='remove_cluster',
            #     # job_flow_id="{{ task_instance.xcom_pull('create_cluster', key='return_value') }}",
            #     job_flow_id=cluster_creator.output,
            #     aws_conn_id='aws_default',
            # )
        '''
        return dag_str

    def get_exist_cluster_dag_code(self) -> str:
        """! Get basic code for dag creation
        Returns:
            A string, containing tailored code for creation of a DAG
        """
        dag_str = '''
        ''' + self.get_dag_conf() + '''
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

            ''' + self.get_stages_str('''cluster_id''') + '''
        '''
        return dag_str

    def get_stages_str(self, job_flow_id: str):
        stages_str = self.get_stages(job_flow_id)
        return stages_str

    def get_stages(self, job_flow_id):
        stages_path = f'{self.curr_path}aws_batch_files/stages'
        folders_with_main_py = []

        specific_jobs_to_run = self.config['specific_jobs_to_run']

        for dirpath, dirnames, filenames in os.walk(stages_path):
            if 'main.py' in filenames:
                job_name = os.path.basename(dirpath)
                if not len(specific_jobs_to_run) or job_name in specific_jobs_to_run:
                    folders_with_main_py.append(job_name)

        print('self.curr_path', self.curr_path)
        print('folders_with_main_py', folders_with_main_py)

        stages = []
        for folder_name in folders_with_main_py:
            stages.append(self.create_stage(job_flow_id, folder_name))

        run_flow = []
        for folder_name in folders_with_main_py:
            run_flow.append(f'step_{folder_name}')
            run_flow.append(f'step_checker_{folder_name}')

        run_flow_str = " >> ".join(run_flow)
        stages_str = "\n".join(stages)
        print('run_flow_str', run_flow_str)

        final_stages = stages_str + f'''
            {run_flow_str}
        '''
        return final_stages

    def get_stages_params(self):
        return '''params={
                    # "BUCKET_NAME": BUCKET_NAME,
                    # "s3_script": s3_script,
                    "start_date": "{execution_date}",
                },
        '''

    def create_stage(self, job_flow_id, name):
        use_cluster_bootstrap = self.config['use_cluster_bootstrap']
        archives = []
        if not use_cluster_bootstrap:
            archives.append('''bucket_path + "/dist/pyspark_venv.tar.gz#venv"''')
        archives.append('''bucket_path + "/dist/" + whl_file_name''')
        return '''
            step_''' + name + ''' = EmrAddStepsOperator(
                task_id='step_''' + name + '''',
                job_flow_id=''' + job_flow_id + ''',
                aws_conn_id='aws_default',
                steps=[{
                    "Name": "Run Spark Job",
                    "ActionOnFailure": "CONTINUE",
                    "HadoopJarStep": {
                        "Jar": "command-runner.jar",
                        "Args": [
                            "spark-submit",
                            "--deploy-mode", "client",
                            "--master", "yarn"
                        ] + spark_properties + [
                            "--archives", ''' + ", ".join(archives) + ''',
                            "--py-files", bucket_path + "/dist/" + whl_file_name,
                            bucket_path + "/aws_batch_files/stages/''' + name + '''/main.py",
                            stage_config, "{{params.start_date}}", "end_time", "params"
                        ]
                    }
                }],
                ''' + self.get_stages_params() + '''
            )

            step_checker_''' + name + ''' = EmrStepSensor(
                task_id='watch_step_''' + name + '''',
                job_flow_id=''' + job_flow_id + ''',
                step_id="{{ task_instance.xcom_pull(task_ids='step_''' + name + '''', key='return_value')[0] }}",
                aws_conn_id='aws_default',
            )
'''

    def demo_stages(self, job_flow_id):
        return '''
            step_get_data = EmrAddStepsOperator(
                task_id='step_get_data',
                job_flow_id=''' + job_flow_id + ''',
                aws_conn_id='aws_default',
                steps=[{
                    "Name": "Run Spark Job",
                    "ActionOnFailure": "CONTINUE",
                    "HadoopJarStep": {
                        "Jar": "command-runner.jar",
                        "Args": [
                            "spark-submit",
                            "--deploy-mode", "client",
                            "--master", "yarn"
                        ] + spark_properties + [
                            # "--archives",bucket_path + "/dist/pyspark_venv.tar.gz#venv"
                            "--py-files", bucket_path + "/dist/" + whl_file_name,
                            bucket_path + "/aws_batch_files/stages/get_data/main.py",
                            stage_config, "{{params.start_date}}", "end_time", "params"
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
                job_flow_id=''' + job_flow_id + ''',
                step_id="{{ task_instance.xcom_pull(task_ids='step_get_data', key='return_value')[0] }}",
                aws_conn_id='aws_default',
            )

            step_get_data >> step_checker
        '''

    def get_dag_conf(self):
        return '''
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

        region = "''' + self.region + '''"
        zone = region + '-b'
        stage_config = \'''' + json_dumps(self.config) + '''\'
        project_id = "''' + self.project_id + '''"
        template_id = "''' + self.template_id + '''"
        bucket_name = "''' + self.bucket_name + '''"
        bucket_path = "''' + self.bucket_path + '''"
        project_name = "''' + self.project_name + '''"
        whl_file_name = "''' + self.project_name + '''.zip"
        target = "''' + self.target + '''"
        cluster_id = "''' + self.cluster_id + '''"
        orig_project_name = project_name
        unique_template_id = "''' + self.unique_template_id + '''"
        spark_properties = ''' + json_dumps(self.spark_properties) + '''
        cluster_config = \'''' + json_dumps(self.cluster_conf) + '''\'
        job_flow_override = json.loads(cluster_config)
        if unique_template_id:
            template_id = template_id + '_' + unique_template_id
            orig_project_name = orig_project_name + '_' + unique_template_id

        extra_dag_job_params = json.dumps({"MODE": "AIRFLOW", "TEST_EXEC_DATE": "{{ next_execution_date }}"})

        now = datetime.now().replace(tzinfo=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        dag_start_date = now - timedelta(days=''' + str(self.dag_start_delay) + ''')

        # STEP 3: Set default arguments for the DAG
        default_dag_args = {
            # 'start_date': dag_start_date,
            'start_date': days_ago(''' + str(self.dag_start_delay) + '''),
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5)
        }
        '''

    def get_cluster_id(self, cluster_name):
        emr_client = boto3.client('emr')
        response = emr_client.list_clusters(ClusterStates=['RUNNING', 'WAITING', 'STARTING', 'BOOTSTRAPPING'])
        clusters = response.get('Clusters', [])
        for cluster in clusters:
            if cluster.get('Name') == cluster_name:
                print("cluster['Id']", cluster['Id'])
                return cluster['Id']
        return ''

    def create_dag(self):
        """! Dag creation.
        This function creates the python file which contains the DAG itself.
        """

        with open(self.file_path, 'w') as dag_text_file:
            if self.cluster_id:
                dag_text_file.write(dedent(self.get_exist_cluster_dag_code()))
            else:
                dag_text_file.write(dedent(self.get_new_cluster_dag_code()))
        print(f"DAG file created: {self.file_path}")

    def import_dag(self, unlink=True):
        """! Dag import.
                This function imports the created DAG file into a GCP composer.
        """

        self.bucket = self.storage_client.Bucket(self.bucket_name)
        parent_path = os.path.abspath(os.path.join(os.getcwd(), 'aws_batch_files'))
        path_local = os.path.join(parent_path, self.file_path)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\', '/')
        # print(self.folder_path + bucket_blob_path)
        # print(self.file_path)
        bucket_final_path = 'dags/' + self.folder_path + bucket_blob_path
        self.bucket.upload_file(path_local, bucket_final_path)
        if unlink:
            os.unlink(self.file_path)

        print(f'uploaded dag successfully to: {bucket_final_path}')

    def delete_dag(self):
        """! Dag deletion.
                This function deletes an existing DAG from a GCP composer.
        """

        self.bucket = self.storage_client.Bucket(self.bucket_name)
        parent_path = os.path.abspath(os.path.join(os.getcwd(), 'aws_batch_files'))
        path_local = os.path.join(parent_path, self.file_path)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\', '/')
        # print(self.folder_path + bucket_blob_path)
        # print(self.file_path)
        bucket_final_path = 'dags/' + self.folder_path + bucket_blob_path
        response = self.bucket.delete_objects(
            Delete={
                'Objects': [
                    {'Key': bucket_final_path}
                ]
            }
        )

        # Check the response to see if the deletion was successful
        if 'Deleted' in response:
            print(f"File '{bucket_final_path}' deleted successfully.")
            print(f'deleted dag successfully to: {bucket_final_path}')
        else:
            print(f"Failed to delete file '{bucket_final_path}'.")

    def instantiate_dag(self, dag_id=None):
        import base64
        dag_id = self.project_name + '_' + self.target + '_dag'
        mwaa_client = boto3.client('mwaa')
        token = mwaa_client.create_cli_token(Name=self.config['environment'])
        url = f"https://{token['WebServerHostname']}/aws_mwaa/cli"
        key = "YOUR_KEY"
        value = "YOUR_VALUE"
        conf = "{\"" + key + "\":\"" + value + "\"}"
        raw_data = "trigger_dag {0} -c '{1}'".format(dag_id, conf)
        body = 'dags trigger ' + dag_id
        headers = {
            'Authorization': 'Bearer ' + token['CliToken'],
            'Content-Type': 'text/plain'
        }
        response = requests.post(url, data=body, headers=headers)

        mwaa_std_err_message = base64.b64decode(response.json()['stderr']).decode('utf8')
        mwaa_std_out_message = base64.b64decode(response.json()['stdout']).decode('utf8')

        print('response.status_code', response.status_code)
        print('mwaa_std_err_message', mwaa_std_err_message)
        print('mwaa_std_out_message', mwaa_std_out_message)
        # Check the response status code
        if response.status_code == 200:
            print(f'instantiate dag successfully: {dag_id}')
            # print("Response content:", response.text)
        else:
            print(f"Failed to instantiate dag '{dag_id}'.")
            # print("Response content:", response.text)


if __name__ == "__main__":
    """! Triggers the creation of the workflow dag, which will instantiate a
    workflow template into an actual workflow, executing it.
    Through this module, we can create a dag file which contains instructions, regarding how to execute the 
    workflow template, and we can also import / remove it into / from an active GCP composer (Only for dev mode)
        Args:
            System argument 1 - Action to be performed on a dag (create, import, delete)
    """

    AWS_PROFILE = ''
    dag_action = ''
    if sys.argv and len(sys.argv) > 1:
        dag_action = sys.argv[1]
    if sys.argv and len(sys.argv) > 2:
        AWS_PROFILE = sys.argv[2]
    dag = Dag(AWS_PROFILE=AWS_PROFILE)

    if dag_action == 'create':
        dag.create_dag()

    elif dag_action == 'import':
        dag.import_dag(unlink=False)

    elif dag_action == 'delete':
        dag.delete_dag()

    if dag_action == 'instantiate':
        # dag_id = ''
        # if sys.argv and len(sys.argv) > 2:
        #     dag_id = sys.argv[2]
        # if not dag_id:
        #     raise Exception('dag_id must be enter')
        # dag_id = 'emr_cluster_management'
        dag.instantiate_dag()
