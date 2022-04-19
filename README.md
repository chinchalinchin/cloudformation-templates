<<<<<<< HEAD
# Infrastructure

The infrastructure supporting the Innovation Lab is provisioned using Infrastructure-as-Code through **CloudFormation**.

```shell
aws cloudformation create-stack
    --stack-name <name>
    --template-body <body>
    --parameters ParameterKey=<key>,ParameterValue=<value> 
                 ParameterKey=<key>,ParameterValue=<value>
                 # ...
```

## Architecture

The setup procedures in this section will provision the following architecture,

![InnoLab Architecture](https://documentation.makpar-innovation.net/_images/innolab_architecture.png)


TODO (@SELAH): description of architecture: VPC, public subnets, private subnets.

# Infrastructure

The infrastructure supporting the Innovation Lab is provisioned through an **Azure DevOps pipeline** hooked into this repository. Resources are configured using [Infrastructure-as-Code](https://en.wikipedia.org/wiki/Infrastructure_as_code). When changes are merged into the `master` branch, this pipeline will pull in the changes into the **Azure** build environment, and then deploy or update the resources defined in the *deployments.yml*. 

## Procedure For Provisioning

You can provision infrastructure locally with the following steps. The pipeline automates, essentially, the exact same steps.

0. Copy the */env/.sample.env* environment file into a new environment file and configure the values. See notes in the sample file for more information on the purpose of each variable,

```shell
cp ./env/.sample.env ./env/.env
```

1. Create a new **CloudFormation** stack template in the */templates/* directory or select an existing template.

2. Add the stack and its parameters to the *deployments.yml* configuration file,

```yaml
MyNewStack:
    template: <template-file-name (just file, no path)>
    parameters:
        - ParameterKey: <parameter1-name>
          ParameterValue: <parameter1-value>
        - ParameterKey: <parameter2-name>
          ParameterValue: <paramter2-value>
        ## ... as many as it takes ... 
```

If the parameter contains sensitive information, such as credentials, put the value in the *.env* file and then reference the variable name in the *deployments.yml* using the `!env` YAML object,

```yaml
MyNewStack:
    template: <template-file-name (just file, no path)>
    parameters:
        - ParameterKey: secretKey
          ParameterValue: !env ENVIRONMENT_SECRET
        ## ... as many as it takes ...
```

In the above example, the template has a parameter `secretKey` in the `Parameters` section, and the *deployments.yml* passes in the value of the environment variable `ENVIRONMENT_SECRET` for this parameter.

**NOTE**: All environment variables that are required locally are also required within the **Azure DevOps** pipeline. [Refer to the official documentation for information on how to provision variables and secrets within the pipeline](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&tabs=yaml%2Cbatch)

3. Invoke the python *deployer.py* script, which in turn will use the **boto3** python library to post the contents of *deployments.yml* to **CloudFormation**,

```shell
python ./src/deploy/deployer.py deploy
```

**NOTE**: In order for this script to succeed, you must have your **AWS CLI** authenticated with an **IAM** account that has permission to deploy resources through **CloudFormation**. Similarly, the **Azure DevOps** pipeline requires an **IAM** account with the appropriate policies attached. 

## Predeployment

To prevent the pipeline from having permission to edit its own permissions, the **IAM** resources for the **Innovation Lab** cloud environment are provisioned outside of the **Azure DevOps** pipeline. Similar to the actual deplyoments, resources that need provisioned before the pipeline takes over can be specified and configured in the *predeployments.yml*. This has a corresponding argument in the *deployer.py* script,

```shell
python ./src/deploy/deployer.py predepoloy

## Development

When adding a new template, before you push to the remote, make sure you run a local linter against templates and scan them for vulnerabilities.

TODO: pre-commit git hook for cfn-linter.

### Security Scan

Use the [snyk iac test](https://docs.snyk.io/snyk-cli/commands/iac-test) CLI utility to analyze the new template configuration,

```shell
./scripts/scan
```

A report will be output into */reports/* as well as printed to console. Address any security vulnerabilites before pushing, as the CI/CD pipeline for provisioning infrastructure will fail if the security scan fails.

### Linting

Ensure the new template is formatted correctly by running the official [CloudFormation linter](https://github.com/aws-cloudformation/cfn-lint) against the new templates,

## Notes

1. Before provisioning the **VPCStack**, ensure the SSH key has been generated locally and imported into the **AWS EC2** keyring,

```shell
aws ec2 import-key-pair --key-name <name-of-key> --public-key-material fileb://<path-to-public-key>
```

**NOTE**: Ensure you import the *public* key, not the *private* key. The *private* key is used to establish the identity of the person initiating an SSH connection.

The bastion host acts as a gateway into the **InnoLab** VPC. After the key has been imported into the bastion host and added to the **SecretsManager**, you can pull the *private* SSH key for tunneling into the bastion host from the **SecretsManager** and initiate a connection with any of the instances in the **VPC** with,

```shell
eval $(ssh-agent -s)
ssh-add ~/.ssh/$KEYNAME
ssh -i $KEYNAME -f -N -L \
      <LOCAL PORT>:<INTERNAL INSTANCE ADDRESS>:<INTERNAL INSTANCE PORT> \
      ec2-user@<NAT BASTION HOST DNS URL> -v
```

2. Before provisioning the **RDSStack**, ensure secrets for the username and password have been created in the **SecretsManager**. See */templates/rds.yml* lines 77 -78 for the secret naming convention.

## Stack Dependencies

The following tables detail the cross stack dependencies between different stacks. The `@env` table implies the stack is deployed each time into a separate environment, i.e. `Dev`, `Staging` or `Prod`. If a stack does not have `@env` in the following table, this implies the stack's resources do not depend on the environment into which it is deployed; in other words, these resources are global. If the stack explicitly declares an environment (as in the case of `SonarStack` and it's cross stack dependency, `VPCStack-Dev`), this implies this stack is only deployed into that environment.

### DevOps Stacks

| Stack | Dependency |
| ----- | ---------- |
| IAMStack | None |
| RepoStack | None |
| DNSStack | None |
| Doc-PipelineStack | IAMStack, RepoStack |
| Frontend-PipelineStack-@env | IAMStack, RepoStack |
| Lambda-PipelineStack-@env | IAMStack, RepoStack |

### Core Stacks

| Stack | Dependency |
| ----- | ---------- |
| CognitoStack-@env | None |
| VPCStack-@env | None |  
| RDSStack-@env | VPCStack-@env, IAMStack | 
| ClusterStack-@env | VPCStack-@env |

### Serverless Stacks

| Stack | Dependency | 
| ----- | ---------- |
| DynamoStack-@env | None | 
| CloudFrontStack | None |
| LambdaStack-@env | VPCStack-@env, RepoStack, CognitoStack-@env, IAMStack |

### Services Stacks

**Note**: These stacks are deployed into the **Fargate ECS** cluster provisioned through the `ClusterStack-@env`.

| Stack | Dependency | 
| ----- | ---------- |
| Frontend-ServiceStack-@env | IAMStack, RepoStack, VPCStack-@env, ClusterStack-@env |
| Backend-ServiceStack-@env | IAMStack, RepoStack, VPCStack-@env, ClusterStack-@env |
| Sonar-ServiceStack | IAMStack, RepoStack, VPCStack-Dev, ClusterStack-Dev |

### Application Stacks

| Stack | Dependency |
| ----- | --------- |
| AlationStack | VPCStack-Dev |

## References

- [AWS CloudFormation Resource Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)
- [Azure DevOps Pipeline](https://docs.microsoft.com/en-us/azure/devops/pipelines/?view=azure-devops)
- [boto3 CloudFormation Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html)
=======
A sweet collection of **CloudFormation** templates.

```
aws cloudformation create-stack
    --stack-name <name>
    --template-body <body>
    --parameters ParameterKey=<key>,ParameterValue=<value> ParameterKey=<key>,ParameterValue=<value>
```

# Cross Stack Dependencies

There are three separate stack sets, the **Account** stack set **DevOps** stack set and the **Application** stack set. 

## Account Stack
| Stack | Dependency |
| IAMStack | None |

## DevOps Stacks
| Stack | Dependency | 
| ----- | ---------- |
| RepoStack | None |
| Pipeline Stack | RepoStack, IAMStack |

## Application Stacks
| Stack  |  Dependency |
| ------ | ----------- |
| CognitoStack | None |
| ECRStack | None | 
| VPCStack-$ENV | None | 
| FrontendStack-$ENV | None |
| RDSStack-$ENV | VPCStack-$ENV, IAMStack | 
| LambdaStack-$ENV | VPCStack-$ENV, ECRStack, CognitoStack, IAMStack |
| GatewayStack-$ENV | UserStack, LambdaStack-$ENV, CognitoStack, IAMStack |
| DNSStack-$ENV | FrontendStack-$ENV, GatewayStack-$ENV |


# Steps

## Configuration

Before any of the stack sets can be stood up, the *.env* environment file needs setup and configured. Copy the sample into a new file and adjust the variables. See *.sample.env* comments for more information on each variable.

```
cp .sample.env .env
```

## Account Stack

Along with the service roles and permissions, this stack creates the developer accounts with the information in the *.env* file. Password resets will be required.

```
./scripts/stacks/devops/iam-stack
```

## DevOps Stack

If the DevOps stack needs stood up (i.e., if the pipeline is provisioned on AWS Codepipeline as opposed to Bitbucket), these stacks should be stood up last, after the Application stack set has been stood up. See [next section](/#application-stack).

```
./scripts/stacks/devops/repo-stack
```

After creating the repositories, the Bitbucket repositories will need cloned into the CodeCommit repositores,

```
./scripts/aws/clone-bb-repos --environments Dev,Staging,Prod
```

Once the repositories are cloned, the final stack, the PipelineStack, can be stood up,

```
./scripts/stacks/devops/pipeline-stack
```

## Application Stack

The first two stacks are independent of the application's environment,

```
./scripts/stacks/app/cognito-stack
./scripts/stacks/app/ecr-stack --components <one | two | three | four | five>
```

After these stacks go up, all subsequent stacks are a function of the environment they are being stood up in,

```
./scripts/stacks/app/vpc-stack --environment <Dev | Prod | Test | Staging>
./scripts/stacks/app/frontend-stack --environment <Dev | Prod | Test | Staging> 
```

At this point, the images for the **Lambda** functions need built for the first time and pushed to ECR.

```
./scripts/stacks/app/rds-stack --environment <Dev | Prod | Test | Staging>
```

At this point, the **RDS** host secret needs passed into AWS **SecretManager**. If an API key is required, add it to the *.env* file and use the following scripts,

```
./scripts/secrets/secret-rds-host --environment <Dev | Prod | Test | Staging>
./scripts/secrets/secret-api-key --environment <Dev | Prod | Test | Staging>
```

Note: The username and password secrets for the RDS are created during the `rds-stack` script, but the host URL secret creation cannot be automated since it doesn't exist until the RDS stack is provisioned. After this is done, then the final sequence of stacks can be stood up,

```
./scripts/stacks/app/lambda-stack --components <one | two | three | four | five> \
                                  --environment <Dev | Prod | Test | Staging>
./scripts/stacks/app/gateway-stack --environment <Dev | Prod | Test | Staging>
./scripts/stacks/app/dns-stack [--dns-exists] \
                                --environment <Dev | Prod | Test | Staging> 
```

All scripts have an optional argument ``--action`` with allowable values of `create` or `update`. The `action` defaults to `create` if not provided. If `update` is passed through the ``--action`` flag, the script will update. NOTE: Some **CloudFormation** configurations *cannot* be updated while the stack is up.

# Notes

1. When creating users through a **CloudFormation** template, you must explicitly tell **CloudFormation** that it's okay to create new users with new permissions. See [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_CreateStack.html). Essentially, when you are creating a stack that involves creating new users, you have to pass in the following flag,

```
aws cloudformation create-stack
    --stack-name UserStack
    --template-body file://path/to/template.yml
    --capabilities CAPABILITY_NAMED_IAM
```

2. In betweens standing up the **ECR** stack and the **Lambda** stack, the images for the **lambdas** will need initialized and pushed to the repo. **lambda** needs the image to exist before it can successfully deploy.


# Documentation
## CloudFormation
### CLI
- [create-stack](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-stack.html)
- [delete-stack](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/delete-stack.html)
- [describe-stacks](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/describe-stacks.html)
- [list-stacks](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/list-stacks.html)

### Template References
- [API Gateway](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ApiGateway.html)
- [ECR](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_ECR.html)
- [IAM](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_IAM.html)
- [Lambda](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_Lambda.html)
>>>>>>> ab838fcb2362895e801e0efaa9a0a1c0aaf1d12f
