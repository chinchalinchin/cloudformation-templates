import argparse
import enum
import sys
from innolab.deploy.deployer import deploy


class Commands(enum.Enum):
    deploy = 'deploy'

    def __str__(self):
        return self.value

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', 
                            type=Commands, 
                            choices=list(Commands), 
                            help="deploy")
    parser.add_argument('-f','--yaml-file', 
                            type=argparse.FileType('r', encoding='UTF-8'),
                            required='deploy' in sys.argv, 
                            help="Absolute path to the YAML deployment configuration file")
    parser.add_argument('-iam', '--iam', 
                            action='store_true',
                            help="Deploy stack with IAM named capabilities")
    args = parser.parse_args()

def main():
    args = parse_args()

    if args.commands:
        deploy(args.yaml_file)

if __name__=="__main__":
    main()