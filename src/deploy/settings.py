import os
import dotenv
import logger

log = logger.get_logger('innolab-cloudformation.deploy.settings')

# DIRECTORY CONFIGURATION
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')
TEMPLATE_DIR=os.path.join(PROJECT_DIR,'templates')
APPLICATION_DIR=os.path.join(TEMPLATE_DIR, 'applications')
PIPELINES_DIR=os.path.join(TEMPLATE_DIR, 'pipelines')
SERVICES_DIR=os.path.join(TEMPLATE_DIR,'services')

# DEPLOYMENT CONFIGURATION
DEPLOYMENT_FILE = os.path.join(PROJECT_DIR, 'deployments.yml')
PREDEPLOYMENT_FILE = os.path.join(PROJECT_DIR, 'predeployments.yml')

# ENVIRONMENT CONFIGURATION

if os.path.exists(os.path.join(ENV_DIR, '.env')):
    dotenv.load_dotenv(os.path.join(ENV_DIR, '.env'))
else:
    log.warning(f'No environment file found in {ENV_DIR}')

APPLICATION = os.environ.setdefault('APPLICATION', 'innolab')
