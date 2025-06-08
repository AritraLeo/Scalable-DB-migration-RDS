# Create CloudFormation template for AWS RDS infrastructure

cloudformation_template = """{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "AWS RDS PostgreSQL with Read Replicas for Supabase Migration",
  "Parameters": {
    "DBInstanceClass": {
      "Type": "String",
      "Default": "db.t3.medium",
      "AllowedValues": [
        "db.t3.micro",
        "db.t3.small",
        "db.t3.medium",
        "db.t3.large",
        "db.r5.large",
        "db.r5.xlarge"
      ],
      "Description": "RDS instance class for primary database"
    },
    "DBName": {
      "Type": "String",
      "Default": "appdb",
      "Description": "Database name",
      "MinLength": "1",
      "MaxLength": "64",
      "AllowedPattern": "[a-zA-Z][a-zA-Z0-9]*"
    },
    "DBUsername": {
      "Type": "String",
      "Default": "postgres",
      "Description": "Database master username",
      "MinLength": "1",
      "MaxLength": "16",
      "AllowedPattern": "[a-zA-Z][a-zA-Z0-9]*"
    },
    "DBPassword": {
      "Type": "String",
      "NoEcho": true,
      "Description": "Database master password (min 8 chars, include upper, lower, number)",
      "MinLength": "8",
      "MaxLength": "41",
      "AllowedPattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\\\d)[a-zA-Z\\\\d@$!%*?&]{8,}$"
    },
    "Environment": {
      "Type": "String",
      "Default": "development",
      "AllowedValues": ["development", "staging", "production"],
      "Description": "Environment name"
    },
    "ProjectName": {
      "Type": "String",
      "Default": "rds-migration",
      "Description": "Project name for resource tagging"
    },
    "EnableReadReplica": {
      "Type": "String",
      "Default": "true",
      "AllowedValues": ["true", "false"],
      "Description": "Enable read replica creation"
    },
    "CrossRegionReplica": {
      "Type": "String",
      "Default": "false",
      "AllowedValues": ["true", "false"],
      "Description": "Create cross-region read replica"
    }
  },
  "Conditions": {
    "CreateReadReplica": {
      "Fn::Equals": [{"Ref": "EnableReadReplica"}, "true"]
    },
    "CreateCrossRegionReplica": {
      "Fn::And": [
        {"Condition": "CreateReadReplica"},
        {"Fn::Equals": [{"Ref": "CrossRegionReplica"}, "true"]}
      ]
    },
    "IsProduction": {
      "Fn::Equals": [{"Ref": "Environment"}, "production"]
    }
  },
  "Resources": {
    "VPC": {
      "Type": "AWS::EC2::VPC",
      "Properties": {
        "CidrBlock": "10.0.0.0/16",
        "EnableDnsHostnames": true,
        "EnableDnsSupport": true,
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-vpc"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "InternetGateway": {
      "Type": "AWS::EC2::InternetGateway",
      "Properties": {
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-igw"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "InternetGatewayAttachment": {
      "Type": "AWS::EC2::VPCGatewayAttachment",
      "Properties": {
        "InternetGatewayId": {"Ref": "InternetGateway"},
        "VpcId": {"Ref": "VPC"}
      }
    },
    "PublicSubnet1": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
        "CidrBlock": "10.0.1.0/24",
        "MapPublicIpOnLaunch": true,
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-public-subnet-1"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "PublicSubnet2": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
        "CidrBlock": "10.0.2.0/24",
        "MapPublicIpOnLaunch": true,
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-public-subnet-2"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "PrivateSubnet1": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
        "CidrBlock": "10.0.11.0/24",
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-private-subnet-1"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "PrivateSubnet2": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
        "CidrBlock": "10.0.12.0/24",
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-private-subnet-2"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "NatGateway1EIP": {
      "Type": "AWS::EC2::EIP",
      "DependsOn": "InternetGatewayAttachment",
      "Properties": {
        "Domain": "vpc",
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-nat-eip-1"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "NatGateway1": {
      "Type": "AWS::EC2::NatGateway",
      "Properties": {
        "AllocationId": {"Fn::GetAtt": ["NatGateway1EIP", "AllocationId"]},
        "SubnetId": {"Ref": "PublicSubnet1"},
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-nat-1"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "PublicRouteTable": {
      "Type": "AWS::EC2::RouteTable",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-public-routes"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "DefaultPublicRoute": {
      "Type": "AWS::EC2::Route",
      "DependsOn": "InternetGatewayAttachment",
      "Properties": {
        "RouteTableId": {"Ref": "PublicRouteTable"},
        "DestinationCidrBlock": "0.0.0.0/0",
        "GatewayId": {"Ref": "InternetGateway"}
      }
    },
    "PublicSubnet1RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "RouteTableId": {"Ref": "PublicRouteTable"},
        "SubnetId": {"Ref": "PublicSubnet1"}
      }
    },
    "PublicSubnet2RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "RouteTableId": {"Ref": "PublicRouteTable"},
        "SubnetId": {"Ref": "PublicSubnet2"}
      }
    },
    "PrivateRouteTable1": {
      "Type": "AWS::EC2::RouteTable",
      "Properties": {
        "VpcId": {"Ref": "VPC"},
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-private-routes-1"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "DefaultPrivateRoute1": {
      "Type": "AWS::EC2::Route",
      "Properties": {
        "RouteTableId": {"Ref": "PrivateRouteTable1"},
        "DestinationCidrBlock": "0.0.0.0/0",
        "NatGatewayId": {"Ref": "NatGateway1"}
      }
    },
    "PrivateSubnet1RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "RouteTableId": {"Ref": "PrivateRouteTable1"},
        "SubnetId": {"Ref": "PrivateSubnet1"}
      }
    },
    "PrivateSubnet2RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "RouteTableId": {"Ref": "PrivateRouteTable1"},
        "SubnetId": {"Ref": "PrivateSubnet2"}
      }
    },
    "DatabaseSecurityGroup": {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupName": {"Fn::Sub": "${ProjectName}-database-sg"},
        "GroupDescription": "Security group for RDS PostgreSQL database",
        "VpcId": {"Ref": "VPC"},
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 5432,
            "ToPort": 5432,
            "SourceSecurityGroupId": {"Ref": "ApplicationSecurityGroup"}
          }
        ],
        "SecurityGroupEgress": [
          {
            "IpProtocol": "-1",
            "CidrIp": "0.0.0.0/0"
          }
        ],
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-database-sg"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "ApplicationSecurityGroup": {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupName": {"Fn::Sub": "${ProjectName}-app-sg"},
        "GroupDescription": "Security group for application layer",
        "VpcId": {"Ref": "VPC"},
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIp": "0.0.0.0/0"
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 443,
            "ToPort": 443,
            "CidrIp": "0.0.0.0/0"
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 3000,
            "ToPort": 3000,
            "CidrIp": "0.0.0.0/0"
          }
        ],
        "SecurityGroupEgress": [
          {
            "IpProtocol": "-1",
            "CidrIp": "0.0.0.0/0"
          }
        ],
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-app-sg"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "DBSubnetGroup": {
      "Type": "AWS::RDS::DBSubnetGroup",
      "Properties": {
        "DBSubnetGroupName": {"Fn::Sub": "${ProjectName}-db-subnet-group"},
        "DBSubnetGroupDescription": "Subnet group for RDS database",
        "SubnetIds": [
          {"Ref": "PrivateSubnet1"},
          {"Ref": "PrivateSubnet2"}
        ],
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-db-subnet-group"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "DBParameterGroup": {
      "Type": "AWS::RDS::DBParameterGroup",
      "Properties": {
        "Family": "postgres15",
        "Description": "PostgreSQL parameter group for optimized performance",
        "Parameters": {
          "shared_preload_libraries": "pg_stat_statements",
          "log_statement": "all",
          "log_min_duration_statement": "1000",
          "checkpoint_completion_target": "0.9",
          "wal_buffers": "16MB",
          "random_page_cost": "1.1",
          "effective_io_concurrency": "200"
        },
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-db-params"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "DBInstance": {
      "Type": "AWS::RDS::DBInstance",
      "DeletionPolicy": "Snapshot",
      "Properties": {
        "DBInstanceIdentifier": {"Fn::Sub": "${ProjectName}-primary"},
        "DBInstanceClass": {"Ref": "DBInstanceClass"},
        "Engine": "postgres",
        "EngineVersion": "15.4",
        "DBName": {"Ref": "DBName"},
        "MasterUsername": {"Ref": "DBUsername"},
        "MasterUserPassword": {"Ref": "DBPassword"},
        "AllocatedStorage": "100",
        "MaxAllocatedStorage": "1000",
        "StorageType": "gp2",
        "StorageEncrypted": true,
        "VPCSecurityGroups": [{"Ref": "DatabaseSecurityGroup"}],
        "DBSubnetGroupName": {"Ref": "DBSubnetGroup"},
        "DBParameterGroupName": {"Ref": "DBParameterGroup"},
        "BackupRetentionPeriod": {"Fn::If": ["IsProduction", 30, 7]},
        "PreferredBackupWindow": "03:00-04:00",
        "PreferredMaintenanceWindow": "sun:04:00-sun:05:00",
        "MultiAZ": {"Fn::If": ["IsProduction", true, false]},
        "PubliclyAccessible": false,
        "EnablePerformanceInsights": true,
        "PerformanceInsightsRetentionPeriod": {"Fn::If": ["IsProduction", 731, 7]},
        "MonitoringInterval": 60,
        "MonitoringRoleArn": {"Fn::GetAtt": ["RDSMonitoringRole", "Arn"]},
        "DeletionProtection": {"Fn::If": ["IsProduction", true, false]},
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-primary-db"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "ReadReplicaDB": {
      "Type": "AWS::RDS::DBInstance",
      "Condition": "CreateReadReplica",
      "Properties": {
        "DBInstanceIdentifier": {"Fn::Sub": "${ProjectName}-replica"},
        "DBInstanceClass": {"Ref": "DBInstanceClass"},
        "SourceDBInstanceIdentifier": {"Ref": "DBInstance"},
        "PubliclyAccessible": false,
        "Tags": [
          {"Key": "Name", "Value": {"Fn::Sub": "${ProjectName}-replica-db"}},
          {"Key": "Environment", "Value": {"Ref": "Environment"}}
        ]
      }
    },
    "RDSMonitoringRole": {
      "Type": "AWS::IAM::Role",
      "Properties": {
        "AssumeRolePolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "",
              "Effect": "Allow",
              "Principal": {
                "Service": "monitoring.rds.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
          ]
        },
        "ManagedPolicyArns": [
          "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
        ],
        "Path": "/"
      }
    }
  },
  "Outputs": {
    "VPCId": {
      "Description": "VPC ID",
      "Value": {"Ref": "VPC"},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-VPC-ID"}}
    },
    "DatabaseEndpoint": {
      "Description": "Primary database endpoint",
      "Value": {"Fn::GetAtt": ["DBInstance", "Endpoint.Address"]},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-DB-Endpoint"}}
    },
    "DatabasePort": {
      "Description": "Database port",
      "Value": {"Fn::GetAtt": ["DBInstance", "Endpoint.Port"]},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-DB-Port"}}
    },
    "ReadReplicaEndpoint": {
      "Condition": "CreateReadReplica",
      "Description": "Read replica endpoint",
      "Value": {"Fn::GetAtt": ["ReadReplicaDB", "Endpoint.Address"]},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-Replica-Endpoint"}}
    },
    "DatabaseSecurityGroupId": {
      "Description": "Database security group ID",
      "Value": {"Ref": "DatabaseSecurityGroup"},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-DB-SG-ID"}}
    },
    "ApplicationSecurityGroupId": {
      "Description": "Application security group ID",
      "Value": {"Ref": "ApplicationSecurityGroup"},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-App-SG-ID"}}
    },
    "PublicSubnet1Id": {
      "Description": "Public subnet 1 ID",
      "Value": {"Ref": "PublicSubnet1"},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-Public-Subnet-1"}}
    },
    "PublicSubnet2Id": {
      "Description": "Public subnet 2 ID",
      "Value": {"Ref": "PublicSubnet2"},
      "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-Public-Subnet-2"}}
    }
  }
}"""

with open('cloudformation-template.json', 'w') as f:
    f.write(cloudformation_template)

# Create deployment script
deployment_script = """#!/bin/bash

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
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

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
        aws cloudformation update-stack \\
            --stack-name $STACK_NAME \\
            --template-body file://$TEMPLATE_FILE \\
            --parameters $PARAMETERS \\
            --capabilities CAPABILITY_IAM \\
            --region $REGION
        
        print_status "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
    else
        print_status "Creating new stack..."
        aws cloudformation create-stack \\
            --stack-name $STACK_NAME \\
            --template-body file://$TEMPLATE_FILE \\
            --parameters $PARAMETERS \\
            --capabilities CAPABILITY_IAM \\
            --region $REGION
        
        print_status "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    fi
    
    print_status "Stack deployment completed successfully!"
}

# Function to get stack outputs
get_outputs() {
    print_status "Getting stack outputs..."
    
    aws cloudformation describe-stacks \\
        --stack-name $STACK_NAME \\
        --region $REGION \\
        --query 'Stacks[0].Outputs' \\
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
esac"""

with open('deploy.sh', 'w') as f:
    f.write(deployment_script)

print("CloudFormation and deployment files created successfully!")
print("Files created:")
print("- cloudformation-template.json (Complete AWS infrastructure)")
print("- deploy.sh (Deployment script with validation)")