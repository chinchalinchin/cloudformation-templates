# TODO: parse deployments yaml, pass arguments into subprocess
# https://stackoverflow.com/questions/13745648/running-bash-script-from-within-python

# alternatively, use boto3 api wrapper around cloudformation directly:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

import os
import pprint
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import settings
from logger import get_logger


log = get_logger('innolab-cloudformation.deploy.deployer')


def get_deployment():
    if os.path.exists(settings.DEPLOYMENT_FILE):
        with open(settings.DEPLOYMENT_FILE, 'r') as infile:
            deployment = yaml.load(infile, Loader=Loader)
        return deployment
    raise FileNotFoundError(f'{settings.DEPLOYMENT_FILE} does not exist')
        
if __name__=="__main__":
    try:
        deployment = get_deployment()
        pprint.pprint(deployment)
        for key,value in deployment.items():
            pass
    except FileNotFoundError as e:
        log.warn(e)