import os
from dotenv import load_dotenv

from logger import get_logger

log = get_logger('innolab-cloudformation.deploy.settings')

# DIRECTORY AND FILE CONFIGURATION
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')
DEPLOYMENT_FILE = os.path.join(PROJECT_DIR, 'deployments.yml')
TEMP_DIR=os.path.join(PROJECT_DIR,'templates','stacks')
# TEMPLATES
TEMPLATE_VPC=os.path.join(TEMP_DIR,'core','vpc.yml')
TEMPLATE_RDS=os.path.join(TEMP_DIR,'core','rds.yml')
TEMPLATE_COGNITO=os.path.join(TEMP_DIR,'core','cognito.yml')
TEMPLATE_IAM=os.path.join(TEMP_DIR,'devops','iam.yml')
TEMPLATE_REPO=os.path.join(TEMP_DIR,'devops','repo.yml')
TEMPLATE_CLUSTER=os.path.join(TEMP_DIR, 'cluster', 'cluster.yml')
TEMPLATE_DYNAMO=os.path.join(TEMP_DIR,'serverless','dynamo.yml')
TEMPLATE_CLOUDFRONT=os.path.join(TEMP_DIR,'serverless','cloudfront.yml')
TEMPLATE_LAMBDA=os.path.join(TEMP_DIR,'serverless','lambda.yml')
TEMPLATE_QLDB=os.path.join(TEMP_DIR,'serverless','qldb.yml')

# ENVIRONMENT VARIABLES
if os.path.exists(os.path.join(ENV_DIR, '.env')):
    load_dotenv(os.path.join(ENV_DIR, '.env'))
    APPLICATION=os.environ.setdefault('APPLICATION', 'innolab').capitalize()
    ENVIRONMENT=os.environ.setdefault('ENVIRONMENT', 'Dev')
    # STACKS
    # GLOBAL STACKS
    IAM_STACK="-".join([APPLICATION, os.environ.setdefault('IAM_STACK', 'IAMStack')])
    REPO_STACK="-".join([APPLICATION, os.environ.setdefault('REPO_STACK', 'RepoStack')])
    CLOUDFRONT_STACK="-".join([APPLICATION, os.environ.setdefault('CLOUDFRONT_STACK', 'CloudFrontStack')])
    # ENVIRONMENT STACKS
    VPC_STACK="-".join([APPLICATION, os.environ.setdefault('VPC_STACK', 'VPCStack'), ENVIRONMENT])
    LAMBDA_STACK="-".join([APPLICATION, os.environ.setdefault('LAMBDA_STACK', 'LambdaStack'), ENVIRONMENT])
    QLDB_STACK="-".join([APPLICATION], os.environ.setdefault('QLDB_STACK', 'QLDBStack'), ENVIRONMENT)
    RDS_STACK="-".join([APPLICATION, os.environ.setdefault('RDS_STACK', 'RDSStack'), ENVIRONMENT])
    DYNAMO_STACK="-".join([APPLICATION, os.environ.setdefault('DYNAMO_STACK', 'DynamoStack'), ENVIRONMENT])
    CLUSTER_STACK="-".join([APPLICATION, os.environ.setdefault('CLUSTER_STACK'), ENVIRONMENT])

    # CONFIGURATION
    RDS_USERNAME=os.getenv('RDS_USERNAME')
    RDS_PASSWORD=os.getenv('RDS_PASSWORD')
    SSH_KEY_NAME="_".join(APPLICATION, os.environ.setdefault('SSH_KEY_NAME', 'tunnel_key'), ENVIRONMENT)
    CERTIFICATE_ID=os.getenv('CERITFICATE_ID')
    HOSTED_ZONE_ID=os.getenv('HOSTED_ZONE_ID')
    DOMAIN=os.environ.setdefault('DOMAIN', 'makpar-innovation.net')
    
else:
    raise FileNotFoundError(f'No environment file found in {ENV_DIR}')