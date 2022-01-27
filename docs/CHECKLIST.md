# Prerequisite Configuration
- [] Get Hosted Zone ID
- [] Get Certificate Arn
- [] Configure Gateway Endpoints

# Stacks

- [] IAMStack
- [] RepoStack
- [] CoverageStack
- [] CognitoStack
- [] VPCStack
- [] RDSStack
- [] LambdaStack
- [] DynamoStack
- [] PipelineStack

## Cluster Stacks
- [] ClusterStack
- [] ServiceStack-@svc

# Non-Stack Operations

- [] generate credentials && configure AWS cli
- [] upload ssh key to profile
- [] push up local repositories to remote
- [] login into ECR && build and push ECR images
    - [] lambda images
    - [] backend image
    - [] frontend image
    - [] build and service images: postgres, node, nginx, pythong
- [] upload database ssh keys to bucket/key manager
- [] upload container .env to environment bucket
- [] upload taskdef/appspec to cluster bucket
- [] add IPs to Bastion host security group rule for SSH tunnels
- [] script to apply branch approval rule to repositores
- [] login into Sonar, change admin password & generate Sonar token
- [] get Cognito auth domain, change verification email password
- [] script for creating/updating secrets
- [] add Null condition to Developer group (see below; TODO: figure out how to get this in the *IAMStack* template)

## Resources

1. Manually add this to the Developer group policy condition,

"Null": {
    "codecommit:References": "false"
}