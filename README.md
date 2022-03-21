# Infrastructure

The infrastructure supporting the Innovation Lab is provisioned using Infrastructure-as-Code through **CloudFormation** and **boto3**. This repository is hooked into an **Azure DevOps pipeline**. When changes are merged into the `master` branch, this pipeline will deploy and update the resources defined through the *deployments.yml*. 

## Procedure For Provisioning

0. Copy the */env/.sample.env* environment file into a new environment file and configure the values. See notes in the sample file for more information on the purpose of each variable,

```shell
cp ./env/.sample.env ./env/.env
```

1. Create a new **CloudFormation** stack template in the */templates/* directory or select an existing template.

2. Add the stack and its parameters to the *deployments.yml* configuration file,

```yaml
MyNewStack:
    template: <tempate-file-name (just file, no path)>
    parameters:
        - ParameterKey: <parameter1-name>
          ParameterValue: <parameter1-value>
        - ParameterKey: <parameter2-name>
          ParameterValue: <paramter2-value>
```

If the parameter contains sensitive information, such as credentials, put the value in the *.env* file and then reference the variable name it in the *deployments.yml* using the YAML object `!env`,

```yaml
MyNewStack:
    template: <tempate-file-name (just file, no path)>
    parameters:
        - ParameterKey: secretKey
          ParameterValue: !env ENVIRONMENT_SECRET
```

In the above example, the template has a parameter `secretKey` in the `Parameters` section, and the *deployments.yml* passed in the value of the environment variable `ENVIRONMENT_SECRET` into this parameter.

## Notes

1. Before provisioning the **VPCStack**, ensure the SSH key has been generated locally and imported in the **AWS EC2** keyring,

```shell
aws ec2 import-key-pair --key-name <name-of-key> --public-key-material fileb://<path-to-public-key>
```

**NOTE**: Ensure you import the *public* key, not the *private* key. The *private* key is used to establish the identity of the person initiating an SSH connection.

2. Before provisioning the **RDSStack**, ensure secrets for the username and password have been created into the **SecretsManager**. See */templates/rds.yml* lines 77 -78 for the secret naming convention.

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