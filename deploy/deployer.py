# TODO: parse deployments yaml, pass arguments into subprocess
# https://stackoverflow.com/questions/13745648/running-bash-script-from-within-python

# alternatively, use boto3 api wrapper around cloudformation directly:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

import yaml

import os
import logging
from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(APP_DIR))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')
