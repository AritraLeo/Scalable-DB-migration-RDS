#!/bin/bash

# AWS RDS Infrastructure Deployment Script
# This script deploys the CloudFormation template for PostgreSQL RDS setup

set -e  # Exit on any error

# Configuration
STACK_NAME="rds-migration-stack"
TEMPLATE_FILE="cloudformation-template.json"
REGION="us-east-1"
PROJECT_NAME="rds-migration"
ENVIRONMENT="development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed and configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi

    print_status "AWS CLI is configured successfully"
}

# Function to validate CloudFormation template
validate_template() {
    print_status "Validating CloudFormation template..."

    if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION; then
        print_status "Template validation successful"
    else
        print_error "Template validation failed"
        exit 1
    fi
}

# Function to check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null
}

# Function to deploy stack
deploy_stack() {
    # Prompt for database password
    echo -n "Enter database master password (min 8 chars, include upper, lower, number): "
    read -s DB_PASSWORD
    echo

    # Validate password
    if [[ ! $DB_PASSWORD =~ ^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9@$!%*?&]{8,}$ ]]; then
        print_error "Password does not meet requirements"
        exit 1
    fi

    print_status "Deploying CloudFormation stack: $STACK_NAME"

    PARAMETERS="ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME"
    PARAMETERS="$PARAMETERS ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    PARAMETERS="$PARAMETERS ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD"
    PARAMETERS="$PARAMETERS ParameterKey=EnableReadReplica,ParameterValue=true"

    if stack_exists; then
        print_status "Stack exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters $PARAMETERS \
            --capabilities CAPABILITY_IAM \
            --region $REGION

        print_status "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
    else
        print_status "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters $PARAMETERS \
            --capabilities CAPABILITY_IAM \
            --region $REGION

        print_status "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    fi

    print_status "Stack deployment completed successfully!"
}

# Function to get stack outputs
get_outputs() {
    print_status "Getting stack outputs..."

    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
}

# Function to delete stack
delete_stack() {
    print_warning "This will delete the entire infrastructure. Are you sure? (y/N)"
    read -r CONFIRM

    if [[ $CONFIRM =~ ^[Yy]$ ]]; then
        print_status "Deleting stack: $STACK_NAME"
        aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION

        print_status "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION

        print_status "Stack deleted successfully!"
    else
        print_status "Stack deletion cancelled"
    fi
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        check_aws_cli
        validate_template
        deploy_stack
        get_outputs
        ;;
    delete)
        check_aws_cli
        delete_stack
        ;;
    outputs)
        check_aws_cli
        get_outputs
        ;;
    validate)
        check_aws_cli
        validate_template
        ;;
    *)
        echo "Usage: $0 {deploy|delete|outputs|validate}"
        echo "  deploy   - Deploy or update the CloudFormation stack"
        echo "  delete   - Delete the CloudFormation stack"
        echo "  outputs  - Show stack outputs"
        echo "  validate - Validate CloudFormation template"
        exit 1
        ;;
esac