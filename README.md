# AWS CloudFormation Environment Setup

A sweet collection of **CloudFormation** templates.

```
aws cloudformation create-stack
    --stack-name <name>
    --template-body <body>
    --parameters ParameterKey=<key>,ParameterValue=<value> ParameterKey=<key>,ParameterValue=<value>
```

# Cross Stack Dependencies

There are three separate stack groups, the **Access** group, the **Application** group and the **DevOps** group. The stacks should be stood up, more or less, in the order listed below, due to cross-stack dependencies, i.e. the *VPCStack* must be stood up before the *RDSStack*, the *LambdaStack* and *SonarStack* must be stood up before the *DNSStack*, etc. 

## Access Stacks
| Stack | Dependency |
| ----- | ---------- |
| IAMStack | None |
| CognitoStack-$env | None |

## Application Stacks
| Stack | Dependency |
| ----- | ---------- |
| RepoStack | None |

### Environment Stacks
| Stack | Dependency | 
| ----- | ---------- |
| DynamoStack-$env | None | 
| VPCStack-$env | None |  
| ECSStack-$env | VPCStack-$env, IAMStack, RepoStack |
| RDSStack-$env | VPCStack-$env, IAMStack | 
| LambdaStack-$env | VPCStack-$env, RepoStack, CognitoStack-$env, IAMStack |

## DevOps Stacks
| Stack | Dependency | 
| ----- | ---------- |
| SonarStack | VPCStack-Dev |

### Environment Stacks
| Stack | Dependency | 
| ----- | ---------- |
| DNSStack-$env | LambdaStack-$env, SonarStack |
| PipelineStack-$env | RepoStack, IAMStack, CognitoStack-$env, DNSStack-$env |

**Note**: *SonarStack* only gets deployed into **Dev** environment.

# Steps

A more detailed version of what follows (with pictures!) can be found on the [Confluence page](https://makpar.atlassian.net/wiki/spaces/IN/pages/358580264/Sandbox+Environment+Setup)

## Configuration

Before any of the stack sets can be stood up, the *.env* environment file needs setup and configured. Copy the sample into a new file and adjust the variables. See *.sample.env* comments for more information on each variable.

```
cp .sample.env .env
```

## Stack Setup

The first stack is the *IAMStack*. Along with the service roles and permissions, this stack creates the developer accounts with the information in the *.env* file. The **MASTER_PASSWORD** environment variable is injected into the template. Password resets will be required on first login.

```
./scripts/stacks/devops/iam-stack
```

There is some leeway with the order of the next few stacks. For the sake of this guide, the next stack will be the *RepoStack*,

```
./scripts/stacks/devops/repo-stack
```

*NOTE*: After creating the repositories, [SSH keys](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html) will need set up on the developer's local machines. The local versions of the repositories will need pushed up; otherwise, the archives on Bitbucket will need cloned into the CodeCommit repositores. Invoke the following script to automate the cloning of each environment,

```
./scripts/aws/clone-bb-repos --environments Dev,Staging,Prod
```

At this point, the images for the *innolab-lambdas* functions, *innolab-backend* and the *innolab-frontend* need built for the first time and pushed to **ECR**. In addition, there are **ECR** repositories to hold images for the Innovation Lab versions of **nginx**, **node**, **postgres** and **python**. These images need tags and pushed to the repositories. They are used in the pipeline to avoid rate limits.

The *VPCStack* can be stood up while the images are building and pushing.

```shell
./scripts/stacks/app/vpc-stack --environment
```

The SonarQube resources can be stood up after the *VPCStack* has been setup,

```shell
./scripts/aws/devops/sonar-stack
```

Once the *SonarStack* goes up, log into SonarQube and reset the default username and password. Generate an API token and store in the **SONAR_TOKEN** variable in the *.env*. This will need stored in the **SecretManager**. Steps for storing secrets are detailed after the *RDSStack* goes up; for now, follow along. 

The Cognito stack can be deployed next,

```shell
./scripts/stacks/app/cognito-stack --environment <Dev | Staging | Prod>
```

Emails will be sent to all users hardcoded into the stack. The *HostedUI* web link in the **Cognito** console under *App Client Settings* can be used to the reset user passwords. It is recommended to updated the message template so future registration email messages include the password reset link. (TODO: configure cloudformation template to edit message template; need **SES** for this.)

Next, the *RDSStack* can be stood up,

```
./scripts/stacks/app/rds-stack --environment <Dev | Prod | Test | Staging>
```

After the *RDSStack* successfully stands up, all the prerequisites for updating the secrets in the **SecretManager** have been met; the **RDS** host secret needs passed into AWS **SecretManager**; The **Sonar** url and token needed added; If an API key is required, add it to the *.env* file and use this time to a the following scripts,

```
./scripts/secrets/secret-rds-host --environment <Dev | Prod | Test | Staging>
./scripts/secrets/secret-sonar-token
./scripts/secrets/secret-sonar-host
./scripts/secrets/secret-api-key --environment <Dev | Prod | Test | Staging>
```

After this is done, then the final sequence of stacks can be stood up,

```
./scripts/stacks/app/lambda-stack --environment <Dev | Prod | Test | Staging>
./scripts/stacks/app/ecs-stack --environment <Dev | Prod | Test | Staging>
./scripts/stacks/app/dns-stack [--dns-exists] \
                                --environment <Dev | Prod | Test | Staging> 
```

All scripts have an optional argument ``--action`` with allowable values of `create` or `update`. The `action` defaults to `create` if not provided. If `update` is passed through the ``--action`` flag, the script will update. NOTE: Some **CloudFormation** configurations *cannot* be updated while the stack is up.

## Pipeline

After all the preceding stacks have been set up and initialized, the final stack, the *PipelineStack*, can be stood up to kick off the CI/CD process. The pipeline has been split into three components, `master`, `app` and `lambdas`. `master` is a pipeline for generating documentation for the coverage **S3** bucket and **CloudFront** distribution provisioned in the **DNSStack**, `app` is a pipeline for building and deploying the services in *ECSStack* into the **Fargate ECS** cluster also provisioned within the stack and `lambdas` is a pipeline for building and deploying the **Lambda** functions in the *LambdaStack*,

```
./scripts/stacks/devops/pipeline-stack --environment <Dev | Prod | Test | Staging> \
                                        --pipeline <master | app | lambdas>
```

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