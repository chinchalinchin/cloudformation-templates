import os
from dotenv import load_dotenv

# DIRECTORY AND FILE CONFIGURATION
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')
DEPLOYMENT_FILE = os.path.join(PROJECT_DIR, 'deployments.yml')
TEMP_DIR=os.path.join(PROJECT_DIR,'templates','stacks')
# ENVIRONMENT STACKS
VPC_STACK=os.path.join(TEMP_DIR,'core','vpc.yml')
RDS_STACK=os.path.join(TEMP_DIR,'core','rds.yml')
COGNITO_STACK=os.path.join(TEMP_DIR,'core','cognito.yml')
IAM_STACK=os.path.join(TEMP_DIR,'devops','iam.yml')
REPO_STACK=os.path.join(TEMP_DIR,'devops','repo.yml')
CLUSTER_STACK=os.path.join(TEMP_DIR, 'cluster', 'cluster.yml')
DYNAMO_STACK=os.path.join(TEMP_DIR,'serverless','dynamo.yml')
CLOUDFRONT_STACK=os.path.join(TEMP_DIR,'serverless','cloudfront.yml')
LAMBDA_STACK=os.path.join(TEMP_DIR,'serverless','lambda.yml')
QLDB_STACK=os.path.join(TEMP_DIR,'serverless','qldb.yml')
# APPLICATION STACKS

# ENVIRONMENT VARIABLES
if os.path.exists(os.path.join(ENV_DIR, '.env')):
    load_dotenv(os.path.join(ENV_DIR, '.env'))