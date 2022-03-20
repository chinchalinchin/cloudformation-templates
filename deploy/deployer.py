# TODO: parse deployments yaml, pass arguments into subprocess
# https://stackoverflow.com/questions/13745648/running-bash-script-from-within-python

# alternatively, use boto3 api wrapper around cloudformation directly:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

import os
import pprint
import yaml
import settings
from logger import get_logger

log = get_logger('innolab-cloudformation.deploy.deployer')

def env_var_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    """Pull YAML node reference from corresponding environment variable"""
    return os.getenv(loader.construct_scalar(node))

def get_loader() -> yaml.SafeLoader:
    """Add environment variable constructor to PyYAML loader.
    """
    loader = yaml.SafeLoader
    loader.add_constructor("!env", env_var_constructor)
    return loader

def get_deployment() -> dict:
    """Parse deployment YAML
    """
    if os.path.exists(settings.DEPLOYMENT_FILE):
        with open(settings.DEPLOYMENT_FILE, 'r') as infile:
            deployment = yaml.load(infile, Loader=get_loader())
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