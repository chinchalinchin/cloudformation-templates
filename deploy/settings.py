import os
from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(APP_DIR))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')
DEPLOYMENT_FILE = os.path.join(PROJECT_DIR, 'deployments.yml')

if os.path.exists(os.path.join(ENV_DIR, '.env')):
    load_dotenv(os.path.join(ENV_DIR, '.env'))