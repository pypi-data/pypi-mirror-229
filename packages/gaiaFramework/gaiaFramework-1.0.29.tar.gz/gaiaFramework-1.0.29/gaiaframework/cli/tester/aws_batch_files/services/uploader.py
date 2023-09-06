import boto3
from boto3.s3.transfer import TransferConfig
import datetime
import sys
import os
import subprocess
from json import load as json_load
# from airflow.api.common.experimental.trigger_dag import trigger_dag
from airflow.api.common import trigger_dag
from airflow.models import DagBag

file_path = os.path.dirname(os.path.abspath(__file__))
curr_path = file_path[:file_path.rfind("aws_batch_files")]
sys.path.append(curr_path)

from aws_batch_files.config.config_base import ConfigBase

class S3Uploader(ConfigBase):
    def __init__(self, AWS_PROFILE=None):
        super().__init__(AWS_PROFILE)
        self.storage_client = boto3.resource('s3')
        self.bucket = self.storage_client.Bucket(self.bucket_name)

    def upload_script(self, local_path, remote_folder):
        remote_key = f"{remote_folder}/spark_script.py"
        self.storage_client.upload_file(local_path, self.bucket_name, remote_key)
        print(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_key}")

    def upload_dag(self, local_path, remote_folder):
        remote_key = f"{remote_folder}/{local_path.split('/')[-1]}"
        self.storage_client.upload_file(local_path, self.bucket_name, remote_key)
        print(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_key}")

    def start_paused_dag(self, dag_id):
        dag_bag = DagBag()
        if dag_id in dag_bag.dags:
            dag = dag_bag.dags[dag_id]
            execution_date = datetime.datetime.now()
            run_id = f"manual__{execution_date.isoformat()}"
            conf = {}  # You can provide any additional configuration if needed
            execution_date_str = execution_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            trigger_dag(dag_id, run_id=run_id, execution_date=execution_date_str, conf=conf)
            print(f"Started DAG run for {dag_id} manually with run_id: {run_id}")
        else:
            print(f"DAG {dag_id} not found in DAG bag.")

    def upload_cluster_init_to_bucket(self, root_dir):
        """! Upload cluster initialization script to a given bucket
                Args:
                    root_dir: Directory in which we search for the cluster initialization script
        """
        name = 'cluster-init-actions.sh'
        path_local = os.path.join(root_dir, name)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\',
                                                                                                             '/')
        self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)
        # blob = self.bucket.blob(self.folder_path + bucket_blob_path)
        # blob.upload_from_filename(path_local)
        # self.gsutils_upload_one_file(path_local, bucket_blob_path)
        print(f'uploaded cluster init script to: {self.folder_path + bucket_blob_path}')

    def upload_requirements_to_bucket(self, root_dir):
        """! Upload cluster initialization script to a given bucket
                Args:
                    root_dir: Directory in which we search for the cluster initialization script
        """
        name = 'requirements_docker.txt'
        path_local = os.path.join(root_dir, name)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\',
                                                                                                             '/')
        self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)
        # blob = self.bucket.blob(self.folder_path + bucket_blob_path)
        # blob.upload_from_filename(path_local)
        # self.gsutils_upload_one_file(path_local, bucket_blob_path)
        print(f'uploaded requirements to: {self.folder_path + bucket_blob_path}')

    def upload_jars_to_bucket(self, root_dir):
        """! Upload relevant jars to a given bucket
            Args:
                root_dir: Directory in which we search for the jars directory
        """

        for path, subdirs, files in os.walk(root_dir + '/jars'):
            for name in files:
                path_local = os.path.join(path, name)
                bucket_blob_path = path_local[path_local.index(self.project_name) +
                                              len(self.project_name):].replace('\\', '/')
                self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)
            # print(path_local)
            # print(bucket_blob_path)
        print('uploaded jars main successfully')

    def upload_stages_main_to_bucket(self, root_dir):
        """! Upload relevant stages to a given bucket
            Args:
                root_dir: Directory in which we search for the stages directory
        """

        for path, subdirs, files in os.walk(root_dir + '/stages'):
            for name in files:
                if name == 'main.py':
                    path_local = os.path.join(path, name)
                    bucket_blob_path = path_local[path_local.index(self.project_name) +
                                                  len(self.project_name):].replace('\\', '/')
                    self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)
                # print(path_local)
                # print(bucket_blob_path)
                # print(name)
        print('uploaded stages main successfully')

    def upload_whl_to_bucket(self, root_dir):
        """! Upload relevant wheel file to a given bucket
            Args:
                root_dir: Directory in which we search for the wheel archive
        """

        parent_path = os.path.abspath(os.path.join(root_dir, ".."))
        dist = parent_path + '/dist'

        # config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
        #                         multipart_chunksize=1024 * 25, use_threads=True)
        onlyfiles = [os.path.join(dist, f) for f in os.listdir(dist) if os.path.isfile(os.path.join(dist, f))]
        for path_local in onlyfiles:
            bucket_blob_path = path_local[path_local.index(self.project_name) +
                                          len(self.project_name):].replace('\\', '/')
            self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)

            # blob = self.bucket.blob(self.folder_path + bucket_blob_path)
            # blob.chunk_size = 1024 * 1024
            # blob.upload_from_filename(path_local)
        # print(path_local)
        # print(project_bucket_folder + bucket_blob_path)

        print(f'uploaded package whl successfully to: {self.folder_path}')

    def upload_files_to_bucket(self, upload_type: str):
        """! Upload jars, stages, cluster init script and wheel file to a given bucket
                Args:
                    upload_type: String reflecting which file type we wish to upload to
                                 bucket (jars, stages, whl, cluster-init, all)
        """
        valid_types = {'all', 'jars', 'stages', 'whl', 'cluster-init', 'requirements'}
        if upload_type not in valid_types:
            print(f"Can't determine file type {upload_type}. "
                  f"Please use one of: 'all', 'jars', 'stages', 'whl', 'cluster-init'")
            return

        print(f'Uploading files of type: {upload_type} to bucket: {self.bucket_name}')

        project_path = os.path.abspath(os.path.join(os.getcwd()))
        batch_files_path = os.path.abspath(os.path.join(os.getcwd(), 'aws_batch_files'))
        script_path = os.path.join(batch_files_path, 'scripts')

        if upload_type == 'all' or upload_type == 'jars':
            self.upload_jars_to_bucket(batch_files_path)
        if upload_type == 'all' or upload_type == 'stages':
            self.upload_stages_main_to_bucket(batch_files_path)
        if upload_type == 'all' or upload_type == 'whl':
            self.upload_whl_to_bucket(batch_files_path)
        if upload_type == 'all' or upload_type == 'cluster-init':
            self.upload_cluster_init_to_bucket(script_path)
        if upload_type == 'all' or upload_type == 'requirements':
            self.upload_requirements_to_bucket(project_path)

    def upload_dag2(self):
        name = 'dag/dag.py'
        parent_path = os.path.abspath(os.path.join(os.getcwd(), 'aws_batch_files'))
        path_local = os.path.join(parent_path, name)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\','/')
        print(self.folder_path + bucket_blob_path)
        self.bucket.upload_file(path_local, self.folder_path + bucket_blob_path)

        print(f'uploaded dag successfully to: {self.folder_path}/{bucket_blob_path}')


if __name__ == "__main__":
    # parent_path = os.path.abspath(os.path.join(os.getcwd(), 'aws_batch_files'))
    # script_path = os.path.join(parent_path, 'scripts')

    AWS_PROFILE = ''
    type = ''
    if sys.argv and len(sys.argv) > 1:
        type = sys.argv[1]
    if not type:
        raise Exception('type must be enter')
    if sys.argv and len(sys.argv) > 2:
        AWS_PROFILE = sys.argv[2]
    s3_uploader = S3Uploader(AWS_PROFILE=AWS_PROFILE)

    s3_uploader.upload_files_to_bucket(type)
    # s3_uploader.upload_dag2()

    # Upload spark_script.py to the "scripts" folder
    # s3_uploader.upload_script('spark_script.py', 'scripts')

    # Upload your_airflow_dag.py to the "dags" folder
    # s3_uploader.upload_dag('dag.py', 'dags')

    # s3_uploader.start_paused_dag('emr_cluster_management')