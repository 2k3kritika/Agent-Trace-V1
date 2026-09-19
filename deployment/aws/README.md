# AgentTrace AWS Deployment

This directory contains the AWS SAM infrastructure for AgentTrace.

## Architecture

React / Amplify
        |
        v
API Gateway
        |
        v
AWS Lambda
        |
        v
FastAPI
        |
        +----------------+
        |                |
        v                v
   DynamoDB             S3
   telemetry          artifacts
   metadata           evidence

## AWS services

AgentTrace uses:

- AWS Lambda
- API Gateway
- DynamoDB
- S3
- IAM

Amazon Bedrock is optional and is not enabled by default.

## Requirements

Install:

- AWS CLI
- AWS SAM CLI
- Python 3.12
- Docker Desktop

Verify:

    aws --version
    sam --version
    docker --version
    python --version

## AWS credentials

Verify the configured AWS identity:

    aws sts get-caller-identity

The deployment should use an IAM identity with only the permissions
required for SAM deployment and AgentTrace resources.

Do not use AdministratorAccess for the runtime Lambda role.

## Build

From the backend directory:

    cd backend

Build the SAM application:

    sam build --template-file deployment/aws/template.yaml

## Deploy

First deployment:

    sam deploy \
      --template-file .aws-sam/build/template.yaml \
      --guided

Choose:

- Stack name: agenttrace-dev
- AWS Region: ap-south-1
- Confirm changes before deploy: Yes
- Allow SAM CLI IAM role creation: Yes
- Disable rollback: No
- Save arguments to samconfig.toml: Yes

For later deployments:

    sam deploy

## Environment

The Lambda receives:

    APP_NAME=AgentTrace
    APP_ENV=dev
    STORAGE_BACKEND=dynamodb
    DYNAMODB_TABLE=agenttrace
    S3_BUCKET=<generated bucket>
    AUTH_ENABLED=true

## Local development

Local development continues using PostgreSQL.

Example:

    STORAGE_BACKEND=postgres

Run:

    alembic upgrade head

Then:

    uvicorn app.main:app --reload

## Local AWS emulation

LocalStack is optional.

It is not required for the first AWS deployment.

Do not introduce LocalStack unless it provides a concrete testing benefit.

## API

After deployment, SAM outputs the API Gateway URL.

The frontend should use:

    VITE_API_BASE_URL=<API Gateway URL>

The FastAPI documentation remains available at:

    <API Gateway URL>/docs

## Cost control

AgentTrace intentionally uses:

- DynamoDB PAY_PER_REQUEST
- Lambda
- S3
- API Gateway

No always-running EC2 instance is required.

No RDS database is required for the AWS deployment.

No ECS or Kubernetes cluster is required.

Bedrock remains disabled unless explicitly enabled.

## Security

The S3 bucket blocks public access.

S3 server-side encryption is enabled.

DynamoDB server-side encryption is enabled.

Runtime Lambda permissions should remain restricted to the
AgentTrace DynamoDB table and AgentTrace S3 bucket.

## Important

Do not manually create the DynamoDB table if it will be managed
by CloudFormation/SAM.

Do not manually create the S3 bucket if it will be managed by
CloudFormation/SAM.

CloudFormation should own these resources so deployments remain
repeatable.