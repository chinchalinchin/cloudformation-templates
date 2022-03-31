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
python ./deploy/deployer.py
```

**NOTE**: In order for this script to succeed, you must have your **AWS CLI** authenticated with an **IAM** account that has permission to deploy resources through **CloudFormation**. Similarly, the **Azure DevOps** pipeline requires an **IAM** account with the appropriate policies attached. 

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
| PipelineStack-@env | RepoStack, IAMStack, CoverageStack, CognitoStack-@env, ClusterStack-@env |


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