A sweet collection of **CloudFormation** templates.

```
aws cloudformation create-stack
    --stack-name <name>
    --template-body <body>
    --parameters ParameterKey=<key>,ParameterValue=<value> ParameterKey=<key>,ParameterValue=<value>
```

# Cross Stack Dependencies

There are two separate stacksets, the **DevOps** stackset and the **Application** stackset. The **DevOps** stacks needs stood up before the **Aplication** stacks go up.

## DevOps Stacks
| Stack | Dependency | 
| ----- | ---------- |
| IAMStack | None |
| RepoStack | None |
| Pipeline Stack | RepoStack, IAMStack |

## Application Stacks
| Stack  |  Dependency |
| ------ | ----------- |
| CognitoStack | None |
| ECRStack | None | 
| VPCStack-$ENV | None | 
| FrontendStack-$ENV | None |
| RDSStack-$ENV | VPCStack-$ENV | 
| LambdaStack-$ENV | VPCStack-$ENV, ECRStack |
| GatewayStack-$ENV | UserStack, LambdaStack-$ENV |
| DNSStack-$ENV | FrontendStack-$ENV, GatewayStack-$ENV |


# Steps

A more detailed version of what follows can be found on the [Confluence page](https://makpar.atlassian.net/wiki/spaces/IN/pages/358580264/Sandbox+Environment+Setup)

## Configuration

Before either stackset can be stood up, the *.env* environment file needs setup and configured. Copy the sample into a new file and adjust the variables. See *.sample.env* comments for more information on each variable.

```
cp .sample.env .env
```

## DevOps Stack

```
./scripts/stacks/devops/iam-stack
./scripts/stacks/devops/repo-stack
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

Then the final stacks can up,

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

2. In betweens standing up the **ECR** stack and the **Lambda** stack, the images for the **lambdas** will need initialized and pushed to the repo. **lambda** needs the image to exist before it can successfull deploy.

3. After the **RDS** stack goes up, the host URL for the RDS instance will need inserted into the AWS **SecretsManager**. Use the script,

```
./scripts/secret-host-rds --environment < Dev | Staging | Test | Prod >
```

Note: The username and password secrets for the RDS are created during the `rds-stack` script, but the host URL secret creation cannot be automated since it doesn't exist until the RDS stack is provisioned.

4. If an API key needs delivered to the **Lambda** function environment, before the **Lambda** stack goes up, update the **API_KEY** environment variable in *.env* environment file and use the script,

```
./scripts/secret-api-key --environment < Dev | Staging | Test | Prod >
```

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
