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


## References
