# Configuration
- [] Get Hosted Zone ID
- [] Get Certificate Arn
- [] Configure Gateway Endpoints
- [] Configure image name in backend repo

# Stacks

- [] IAMStack
- [] RepoStack
- [] ECRStack
- [] VPCStack
- [] FrontendStack
- [] RDSStack
- [] CognitoStack
- [] LambdaStack
- [] SonarStack
- [] GatewayStack
- [] DNSStack
- [] PipelineStack

# Non-Stack Operations

- [] generate credentials && configure AWS cli
- [] build ECR images
- [] upload ssh key to profile
- [] upload database ssh keys to bucket
- [] add IPs to Bastion host security group rule for SSH
- [] script to initialize coverage bucket
- [] script for cloning repositories
- [] script for branch rules
- [] script for RDS host secret 
- [] login into Sonar and change admin password
- [] generate Sonar token
- [] script for Sonar host secret
- [] script for Sonar token secret
- [] add Null condition to Developer group (see below)
- [] get Cognito auth domain, change password and add to secrets
- [] tag local *postgres* image with ECR and push for pipeline to use

### Conditionally Required
- [] script to add API key secret

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