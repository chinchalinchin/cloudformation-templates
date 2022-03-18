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

![InnoLab Architecture](/docs/innolab_architecture.png)

## Cross Stack Dependencies

There are four separate stack groups, the **DevOps** group, the **Core** group, the **Serverless** group and the **Cluster** group. Due to cross-stack dependencies, the stacks must be stood up so that independent stacks go up before dependent stacks, i.e. the *VPCStack* must be stood up before the *RDSStack*, the *RepoStack* should be stood up before the *ClusterStack*, etc. 

**NOTE**: The *DNSStack* only needs stood up if a HostedZone and an ACM Certificate need provisioned; if these already exist, ignore this stack.

### DevOps Stacks
| Stack | Dependency |
| ----- | ---------- |
| IAMStack | None |
| RepoStack | None |
| DNSStack | None |
| CoverageStack | None |
| PipelineStack-@env | RepoStack, IAMStack, CoverageStack, CognitoStack-@env, ClusterStack-@env |

### Core Stacks
| Stack | Dependency |
| ----- | ---------- |
| CognitoStack-@env | None |
| VPCStack-@env | None |  
| RDSStack-@env | VPCStack-@env, IAMStack | 

### Serverless Stacks
| Stack | Dependency | 
| ----- | ---------- |
| DynamoStack-@env | None | 
| LambdaStack-@env | VPCStack-@env, RepoStack, CognitoStack-@env, IAMStack |

### Cluster Stacks
| Stack | Dependency | 
| ----- | ---------- |
| ClusterStack-@env | VPCStack-@env |

**Service Stack**
| Stack | Dependency | 
| ----- | ---------- |
| Frontend-ServiceStack-@env | IAMStack, RepoStack, VPCStack-@env, ClusterStack-@env |
| Backend-ServiceStack-@env | IAMStack, RepoStack, VPCStack-@env, ClusterStack-@env |
| Sonar-ServiceStack | IAMStack, RepoStack, VPCStack-Dev, ClusterStack-Dev |

**NOTE:** The *Sonar-ServiceStack* is only deployed into the **Dev** environment. 

## Configuration

Before any of the stack sets can be stood up, the *.env* environment file needs setup and configured. Copy the sample into a new file and adjust the variables. See *.sample.env* comments for more information on each variable.

```
cp ./env/.sample.env ./env/.env
```

## Core Setup

**NOTE**: All scripts in the following section have an optional argument `--action` with allowable values of `create`, `delete` or `update`. The `action` defaults to `create` if not provided. If `update` is passed through the ``--action`` flag, the script will update. NOTE: Some **CloudFormation** configurations *cannot* be updated while the stack is up.

The first series of stacks is made up of the *IAMStack*, *RepoStack*, *CoverageStack*, *VPCStack* and *CognitoStack*. None of these stacks have any cross stack dependencies, thus they can be stood up in parallel.

```shell
./scripts/stacks/devops/iam-stack
./scripts/stacks/devops/repo-stack
./scripts/stacks/devops/coverage-stack
./scripts/stacks/core/vpc-stack --environment <Dev | Prod | Test | Staging>
./scripts/stacks/core/cognito-stack --environment <Dev | Prod | Test | Staging>
```

After creating the user accounts and source code repositories, [SSH keys](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html) will need set up on the developer's local machines and uploaded to the **AWS IAM** console. The local versions of the repositories will need pushed up to **CodeCommit** and images for the *innolab-lambdas* functions, *innolab-backend* and the *innolab-frontend* applications need built for the first time and pushed to **ECR**. See their respective sections on the sidebar menu. 

In addition, there are **ECR** repositories to hold images for the Innovation Lab versions of **nginx**, **node**, **postgres** and **python**. These images need tagged and pushed to the repositories as well; They are used in the pipeline to avoid pull nrate limits.

Emails will be sent to all users hardcoded into the *CognitoStack*. The *HostedUI* web link in the **Cognito** console under *App Client Settings* can be used to the reset user passwords. It is recommended to updated the message template so future registration email messages include the password reset link. (TODO: configure cloudformation template to edit message template; need **SES** for this.)

During the provisioning of the *VPCStack*, an SSH key for tunneling into the VPC was generated in your user's */.ssh/* folder. This key will need distributed to anyone who needs access to any of the deployed instances. The IP of the user who is tunneling into the VPC will need added to the Bastion Host security group.

### RDS 

Afer the *VPCStack* goes up, the process to stand up the RDS can be started. First, secrets will need provisioned for the RDS credentials. These secrets are used within the */templates/core/rds/* to populate the administrator user account for the RDS. The **RDS_USERNAME** and **RDS_PASSWORD** get passed to **AWS SecretManager** through the following script,

```shell
./scripts/secrets/secret-rds-creds --environment <Dev | Prod | Test | Staging>
```

The secrets must exist in the **SecretManager** before the *RDSStack* goes up. Once they have been successfully created or updated, invoke the following script,

```shell
./scripts/stacks/core/rds-stack --environment <Dev | Prod | Test | Staging >
```

After the *RDSStack* goes up, the RDS will get assigned a host URL and this value will be outputted through **CloudFormation** (it can be seen in the `aws cloudformation describe-stack` command). Following best practices, this sensitive piece of information also needs added to the **SecretManager**,

```shell
./scripts/secrets/secret-rds-host --environment <Dev | Prod | Test | Staging>
```

## Serverless Components

A stack of Lambda functions with various integrations in **CloudWatch** and **APIGateway** can be stood up with,

```shell
./scripts/stacks/serverless/lambda-stack --environment <Dev | Prod | Test | Staging>
```

There are examples of **Lambda** integrations in the comments at the end of the the */templates/serverless/lambda.yml* file.

A stack for a **DynamoDB** table with a partition key can be stood up with the following script,

```shell
./scripts/stacks/serverless/dynamo-stack --environment <Dev | Prod | Test | Staging> \
                                            --table-name <table_name>
                                            --partition-key <partition_key>
```

**Note**: a sort key can optionally be specified through the `--sort-key` flag.

## Fargate Cluster 

The *ClusterStack* can be stood up anytime after the *VPCStack* stack goes up. This stack will provision the core [Fargate](https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorial-ecs-deployment.html) infrastructure necessary for services to be deployed to the cluster. Each individual service stack (see below) will still need service-specific resources, but each service will deploy onto this cluster and use the [service namespace](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html) provisioned within the template.

```shell
./scripts/stacks/cluster/cluster-stack --environment <Dev | Prod | Test | Staging>
```

### Services

Finally, once the rest of the stacks, beside the *PipelineStack* have been stood up, services can be deployed to the cluster, using the template yamls in the */templates/cluster/services/* directory. Currently, there are three services defined: `backend`, `frontend` and `sonar`. A single script can deploy any one of these services at a time, by providing the runtime information to the script,

```shell
./scripts/stacks/cluster/service-stack --environment <Dev | Prod | Test | Staging>
                                        --service <sonar | backend | frontend>
                                        --port <port>
```

The image used to deploy the service will default to using a tag with a value equal to the environment, i.e. if `--environment Dev --service backend`, the service will deploy the backend image tagged with `Dev`. Optionally, a different tag can be specified for the service,

```
./scripts/stacks/cluster/service-stack --environment <Dev | Prod | Test | Staging>
                                        --service <sonar | backend | frontend>
                                        --port <port>
                                        --tag <tag>
```

## Secrets

There are scripts for creating various secrets the application cluster may need. The scripts are used to enforce a naming convention, so the applications will be able to construct the secret name based on their deployment and environment.

```
./scripts/secrets/secret-sonar-creds
./scripts/secrets/secret-atlassian-token
./scripts/secrets/secret-api-creds --environment <Dev | Prod | Test | Staging>
./scripts/secrets/secret-api-key --environment <Dev | Prod | Test | Staging>
```

## Pipeline

After all the preceding stacks have been set up and initialized, the final stack, the *PipelineStack*, can be stood up to kick off the CI/CD process. The pipeline has been split into four components, `master`, `app`, `lambda` and `cloudformation`. `master` is a pipeline for generating documentation for the coverage **S3** bucket and **CloudFront** distribution provisioned in the **CoverageStack**, `app` is a pipeline for building and deploying the services in *ECSStack* into the **Fargate ECS** cluster also provisioned within the stack,`lambda` is a pipeline for building and deploying the **Lambda** functions in the *LambdaStack*, and `cloudformation` is a pipeline for deploying changes to the AWS infrastructure. The pipelines can be stood up with the following script,

```
./scripts/stacks/devops/pipeline-stack --environment <Dev | Prod | Test | Staging> \
                                        --pipeline <master | app | lambda | cloudformation>
```

Unforunately, in the case of the `app` pipeline, this process cannot be completely automated as of yet. The build stage can be stood up entirely through a **CloudFormation** template, but the deploy stage has several steps that need to be complete before the pipeline will perform *blue-green* deployments  It requires setting up deployment groups and deployment stages through the console. 

## Automated Deployments

The `cloudformation` pipeline is hooked into the master branch of this repository, *innolab-cloudformation*. When changes are pushed or merged to `master`, **CodePipeline** will pull the template changes into **CodeBuild**, scan the proposed changes for security vulnerability and update the stacks defined the *deployments.yml* in the project's root directory. 

The *deployments.yml* determines which stacks will be updated through the pipeline. The pipeline will parse the YAML and pass the key-value pairs underneath a given stack entry into the script that deploys that stack. In other words, the configuration,

```yaml
rds-stack:
  environment: Dev
  type: postgres
  port: 5432
```

Will ensure the pipeline posts the stack update to the **rds-stacks**.


## Notes

1. **ECR** repositories and **S3** buckets must be emptied before their containing stacks can be deleted.

2. **EC2** keypairs for the bastion host are not deleted when the stack is deleted. They must be manually deleted. First, grab and then delete the key-name,

```shell
aws ec2 describe-key-pairs
aws ec2 delete-key-pair --key-name $KEY_NAME
```