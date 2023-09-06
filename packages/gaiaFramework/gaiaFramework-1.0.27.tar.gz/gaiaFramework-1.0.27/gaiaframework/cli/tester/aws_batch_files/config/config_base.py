import sys
import os
from json import load as json_load

import boto3

class ConfigBase:

    def __init__(self, AWS_PROFILE=None):

        if AWS_PROFILE:
            boto3.setup_default_session(profile_name=AWS_PROFILE)

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
            self.config['user_id'] = self.user_id

        self.bucket_name = stage_config['bucket_name']
        self.project_id = stage_config['project_id']
        self.project_name = stage_config['project_name']
        self.target = stage_config['target']
        self.unique_template_id = stage_config['unique_template_id']
        self.region = stage_config['region']
        self.zone = self.region + '-b'  # TODO: Check if we can configure this as well
        self.template_id = stage_config['template_id']
        self.unique_iteration_id = stage_config['unique_iteration_id']
        self.extra_job_params = stage_config['extra_job_params']
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