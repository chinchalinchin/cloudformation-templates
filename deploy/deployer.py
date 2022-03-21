# TODO: parse deployments yaml, pass arguments into subprocess
# https://stackoverflow.com/questions/13745648/running-bash-script-from-within-python

# alternatively, use boto3 api wrapper around cloudformation directly:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

import boto3
import os
import pprint
import yaml
import settings
from logger import get_logger

log = get_logger('innolab-cloudformation.deploy.deployer')

ACTIVE_STACKS=[
    'CREATE_IN_PROGRESS', 
    'CREATE_COMPLETE', 
    'ROLLBACK_IN_PROGRESS', 
    'ROLLBACK_COMPLETE', 
    'DELETE_IN_PROGRESS', 
    'UPDATE_IN_PROGRESS', 
    'UPDATE_COMPLETE', 
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 
    'UPDATE_ROLLBACK_IN_PROGRESS', 
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 
    'UPDATE_ROLLBACK_COMPLETE'
]

def env_var_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    """Pull YAML node reference from corresponding environment variable

    :param loader: YAML Serializer
    :type loader: yaml.SafeLoader
    :param node: Node in the YAML tree
    :type node: yaml.nodes.ScalarNode
    :return: Environment variable value with given `node` key.
    :rtype: str
    """
    return os.getenv(loader.construct_scalar(node))

def get_loader() -> yaml.SafeLoader:
    """Add environment variable constructor to PyYAML loader.
    :return: YAML serializer
    :rtype: :class:`yaml.SafeLoader`
    """
    loader = yaml.SafeLoader
    loader.add_constructor("!env", env_var_constructor)
    return loader

def get_deployment() -> dict:
    """Parse deployment YAML

    :return: deployment configurations
    :rtype: dict
    """
    if os.path.exists(settings.DEPLOYMENT_FILE):
        with open(settings.DEPLOYMENT_FILE, 'r') as infile:
            deployment = yaml.load(infile, Loader=get_loader())
        return deployment
    raise FileNotFoundError(f'{settings.DEPLOYMENT_FILE} does not exist')

def get_client() -> boto3.client:
    """ Factory function for **boto3 CloudFormation** client
    :return: **CloudFormation** client
    :rtype: :class:`boto3.client`
    """
    return boto3.client('cloudformation')

def get_stack_names() -> list:
    """Return list of currently active **CloudFormation** stacks.
    :return: Stack names
    :rtype: list
    """
    stacks = get_client().list_stacks(
        StackStatusFilter=ACTIVE_STACKS
    )['StackSummaries']
    return [ stack['StackName'] for stack in stacks]

def update_stack(stack: str, deployment: dict) -> dict:
    """Update the given `stack` with the given `deployment` configuration

    :param stack: Name of the stack to be updated.
    :type stack: str
    :param deployment: `dict` containing the deployment configuration
    :type deployment: dict
    :return: **CloudFormation** response
    :rtype: dict
    """
    log.info('Updating stack %s', stack)
    parameters = deployment['parameters']
    client = get_client()
    return client.update_stack(
        StackName=os.path.join(settings.TEMPLATE_DIR, stack),
        Parameters=parameters,
        Capabilities=[
            'CAPABILITY_IAM',
            'CAPABILITY_NAMED_IAM',
            'CAPABILITY_AUTO_EXPAND',
        ],
        Tags=[{
            'Key': 'Application',
            'Value': settings.APPLICATION
        }]
    )

def create_stack(stack: str, deployment: dict) -> dict:
    log.info('Updating stack %s', stack)
    parameters = deployment['parameters']
    client=get_client()
    client.create_stack(
        StackName=os.path.join(settings.TEMPLATE_DIR, stack),
        Parameters=parameters,
        Capabilities=[
            'CAPABILITY_IAM',
            'CAPABILITY_NAMED_IAM',
            'CAPABILITY_AUTO_EXPAND',
        ],
        Tags=[{
            'Key': 'Application',
            'Value': settings.APPLICATION
        }]
    )

if __name__=="__main__":
    try:
        stack_deployments, stack_names = get_deployment(), get_stack_names()
        pprint.pprint(stack_deployments)
        for stack, deployment in stack_deployments.items():
            if stack in stack_names:
                update_stack(stack, deployment)
            else:
                create_stack(stack, deployment)
        print(get_stack_names())

    except FileNotFoundError as e:
        log.warn(e)