A sweet collection of **CloudFormation** templates.

```
aws cloudformation create-stack
    --stack-name <name>
    --template-body <body>
    --parameters ParameterKey=<key>,ParameterValue=<value> ParameterKey=<key>,ParameterValue=<value>
```
# Steps


```
cp .sample.env .env
source .env
./scripts/users-stack
./scripts/vpc-stack --environment <Dev | Prod | Test>
./scripts/rds-stack --environment <Dev | Prod | Test>
./scripts/ecr-stack --components <one | two | three | four >
# Build images and push to ECR; use ./scripts/docker/build-images from lambda-pipeline repo
./scripts/lambda-stack --components <one | two | three | four> --environment <Dev | Prod | Test>
# API Gateway stack goes here
```

# Notes

1. When creating users through a **CloudFormation** template, you must explicitly tell **CloudFormation** that it's okay to create new users with new permissions. See [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_CreateStack.html). Essentially, when you are creating a stack that involves creating new users, you have to pass in the following flag,

```
aws cloudformation create-stack
    --stack-name UserStack
    --template-body file://path/to/template.yml
    --capabilities CAPABILITY_NAMED_IAM
```

2. `VPCStack-{environment}` and `UserStack` have no dependencies on other stacks. `ECRStack-{component}` has a dependency on `UserStack` through the pipeline user. `LambdaComponentStack-{component}-{environment}` has a dependency on `UserStack` through the lambda executor role, `VPCStack-${environment}` through the database security group and `ECRStack-{component}` through the **ECR** that holds the lambda image. `RDSStack-${environment}` has a dependency on `VPCStack-${environment}` through the database security group and subnet group. 

3. In betweens standing up the **ECR** stack and the **Lambda** stack, the images for the **lambdas** will need initialized and pushed to the repo. **lambda** needs the image to exist before it can successfull deploy.

4. the **ECR** stack and the **User** stack are independent of the environment being provisioned. The differences in the environment images is managed through tags in the **ECR** repo, while users and roles are global resources available in all environments.

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
