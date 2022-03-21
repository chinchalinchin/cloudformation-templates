# TODO: parse deployments yaml, pass arguments into subprocess
# https://stackoverflow.com/questions/13745648/running-bash-script-from-within-python

# alternatively, use boto3 api wrapper around cloudformation directly:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

import boto3
import botocore
import os
import pprint
import yaml
import settings
import time
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
IN_PROGRESS_STACKS=[
    'CREATE_IN_PROGRESS', 
    'UPDATE_IN_PROGRESS', 
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
]

def env_var_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    """Pull YAML node reference from corresponding environment variable

    :param loader: YAML Serializer
    :type loader: :class:`yaml.SafeLoader`
    :param node: Node in the YAML tree
    :type node: :class:`yaml.nodes.ScalarNode`
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
    """Parse *deployments.yml*

    :return: deployment configuratio
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

def get_stack_names(in_progress: bool = False) -> list:
    """Return list of currently active **CloudFormation** stacks.

    :param in_progress: Flag to filter stacks by `*_IN_PROGRESS` only.
    :type in_progress: bool
    :return: Stack names
    :rtype: list
    """
    if in_progress: 
        filter = IN_PROGRESS_STACKS
    else:
        filter = ACTIVE_STACKS
    stacks = get_client().list_stacks(
        StackStatusFilter=filter
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

    try:
        with open(os.path.join(settings.TEMPLATE_DIR, deployment['template']),'r') as infile:
            template = infile.read()
    except FileNotFoundError as e:
        log.warning(e)
        return e

    client = get_client()
    try:
        return client.update_stack(
            StackName=stack,
            TemplateBody=template,
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
    except botocore.exceptions.ClientError as e:
        log.warning(e)
        return e

def create_stack(stack: str, deployment: dict) -> dict:
    """Create the given `stack` with the given `deployment` configuration

    :param stack: Name of the stack to be updated.
    :type stack: str
    :param deployment: `dict` containing the deployment configuration
    :type deployment: dict
    :return: **CloudFormation** response
    :rtype: dict
    """
    log.info('Creating stack %s', stack)
    parameters = deployment['parameters']

    try:
        with open(os.path.join(settings.TEMPLATE_DIR, deployment['template']),'r') as infile:
            template = infile.read()
    except FileNotFoundError as e:
        log.warning(e)
        return e

    client = get_client()
    try:
        return client.create_stack(
            StackName=stack,
            TemplateBody=template,
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
    except botocore.exceptions.ClientError as e:
        log.warning(e)
        return e

def deploy():
    """Application entrypoint. This function orchestrates the deployment.
    """
    stack_deployments, stack_names = get_deployment(), get_stack_names()

    for stack, deployment in stack_deployments.items():
        if stack in stack_names:
            result = update_stack(stack, deployment)
        else:
            result = create_stack(stack, deployment)

        log.info(result)

        while stack in get_stack_names(in_progress=True):
            log.info('Waiting on %s...', stack)
            time.sleep(10)

if __name__=="__main__":
    deploy()