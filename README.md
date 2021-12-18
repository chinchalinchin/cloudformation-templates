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
| ----- | --------- |
| IAMStack | None |

## DevOps Stacks
| Stack | Dependency | 
| ----- | ---------- |
| RepoStack | None |
| PipelineStack | RepoStack, IAMStack, CognitoStack, DNSStack |
| SonarStack | VPCStack |

## Application Stacks
| Stack  |  Dependency |
| ------ | ----------- |
| CognitoStack | None |
| VPCStack | None | 
| RDSStack-Dev, RDSStack-Staging, RDSStack-Prod | VPCStack, IAMStack | 
| LambdaStack | VPCStack, RepoStack, CognitoStack, IAMStack |
| DNSStack | LambdaStack, SonarStack |

# Steps

A more detailed version of what follows (with pictures!) can be found on the [Confluence page](https://makpar.atlassian.net/wiki/spaces/IN/pages/358580264/Sandbox+Environment+Setup)

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

The SonarQube resources can be stood up after the **VPCStack** has been setup,

```
./scripts/aws/devops/sonar-stack
```

## Application Stack

The first two stacks are independent of the application's environment,

```
./scripts/stacks/app/cognito-stack
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

## Pipeline

After all the preceding stacks have been set up and initialized, the final stack, the PipelineStack, can be stood up to kick off the CI/CD process,

```
./scripts/stacks/devops/pipeline-stack
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

# TODOS

1. distribute jira integration across stacks. 
2. simplify lambda and gateway stack into lambda and lambda-integration stack. extend the possible use cases of lambda in a single stack.