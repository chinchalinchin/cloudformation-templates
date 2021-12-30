# Configuration
- [x] Get Hosted Zone ID
- [x] Get Certificate Arn
- [] Configure Gateway Endpoints
- [x] Configure image name in lambda repo

# Stacks

- [x] IAMStack
- [x] RepoStack
- [x] ECRStack
- [x] VPCStack
- [x] FrontendStack
- [x] RDSStack
- [x] CognitoStack
- [x] LambdaStack
- [x] SonarStack
- [x] GatewayStack
- [x] DNSStack
- [] PipelineStack

# Non-Stack Operations

- [x] generate credentials && configure AWS cli
- [x] build ECR images
- [x] upload ssh key to profile
- [x] upload database ssh keys to bucket
- [x] add IPs to Bastion host security group rule for SSH
- [x] script to initialize coverage bucket
- [x] script for cloning repositories
- [x] script for branch rules
- [x] script for RDS host secret 
- [x] login into Sonar and change admin password
- [x] generate Sonar token
- [x] script for Sonar host secret
- [x] script for Sonar token secret
- [x] add Null condition to Developer group (see below)
- [x] get Cognito auth domain, change password and add to secrets
- [x] tag local *postgres* image with ECR and push for pipeline to use

### Conditionally Required
- [x] script to add API key secret

# Presentation

- [] Screenshot Sonar project tab
- [] Screenshot Sonar analysis tab
- [] Screenshot API Gateway Integration tab
- [] Screenshot Pipeline

## Resources

1. Manually add this to the Developer group policy condition,

"Null": {
    "codecommit:References": "false"
}