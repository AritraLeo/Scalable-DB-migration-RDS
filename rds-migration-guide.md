# Supabase to AWS RDS PostgreSQL Migration Guide

## Overview
This guide provides step-by-step instructions for migrating from Supabase PostgreSQL to AWS RDS PostgreSQL with read replicas, including a complete Node.js/TypeScript implementation.

## Architecture Components

### Primary Infrastructure
- **AWS RDS PostgreSQL** - Primary database instance
- **Read Replicas** - For read scaling and load distribution
- **VPC & Security Groups** - Network isolation and security
- **Application Layer** - Node.js/TypeScript with connection pooling

## Phase 1: Pre-Migration Assessment

### 1.1 Analyze Current Supabase Setup
```bash
# Connect to Supabase and gather information
psql "postgresql://[username]:[password]@[host]:5432/[database]"

# Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));

# List all tables and their sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check for extensions
SELECT * FROM pg_extension;
```

### 1.2 Identify Tables for Read Replicas
- High-read volume tables
- Reporting/analytics tables
- User-facing content tables

## Phase 2: AWS Infrastructure Setup

### 2.1 Create VPC and Security Groups
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=rds-migration-vpc}]'

# Create subnets in different AZs
aws ec2 create-subnet --vpc-id vpc-xxxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b

# Create security group for RDS
aws ec2 create-security-group --group-name rds-security-group --description "Security group for RDS PostgreSQL" --vpc-id vpc-xxxxxx
```

### 2.2 Create RDS Subnet Group
```bash
aws rds create-db-subnet-group \
    --db-subnet-group-name rds-subnet-group \
    --db-subnet-group-description "Subnet group for RDS PostgreSQL" \
    --subnet-ids subnet-xxxxxx subnet-yyyyyy
```

### 2.3 Create Primary RDS Instance
```bash
aws rds create-db-instance \
    --db-instance-identifier my-postgres-primary \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password SecurePassword123! \
    --allocated-storage 100 \
    --storage-type gp2 \
    --storage-encrypted \
    --db-subnet-group-name rds-subnet-group \
    --vpc-security-group-ids sg-xxxxxx \
    --backup-retention-period 7 \
    --enable-performance-insights \
    --monitoring-interval 60 \
    --auto-minor-version-upgrade
```

## Phase 3: Database Migration

### 3.1 Export from Supabase
```bash
# Create compressed dump
pg_dump "postgresql://[username]:[password]@[supabase-host]:5432/[database]" \
    -Fc \
    -v \
    --schema=public \
    --no-owner \
    --no-acl \
    -f supabase_migration.dump

# For large databases, use parallel dump
pg_dump "postgresql://[username]:[password]@[supabase-host]:5432/[database]" \
    -Fd \
    -v \
    -j 4 \
    --schema=public \
    --no-owner \
    --no-acl \
    -f supabase_migration_dir/
```

### 3.2 Import to AWS RDS
```bash
# Restore from compressed dump
pg_restore -v \
    -h [rds-endpoint] \
    -U postgres \
    -d [database-name] \
    --no-owner \
    --no-acl \
    -j 4 \
    supabase_migration.dump

# For directory format
pg_restore -v \
    -h [rds-endpoint] \
    -U postgres \
    -d [database-name] \
    --no-owner \
    --no-acl \
    -j 4 \
    supabase_migration_dir/
```

### 3.3 Data Validation
```sql
-- Compare record counts
SELECT 'users' as table_name, count(*) as count FROM users
UNION ALL
SELECT 'orders' as table_name, count(*) as count FROM orders;

-- Verify indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';

-- Check constraints
SELECT conname, contype FROM pg_constraint WHERE connamespace = 'public'::regnamespace;
```

## Phase 4: Read Replica Setup

### 4.1 Create Read Replicas
```bash
# In-region read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier my-postgres-replica-1 \
    --source-db-instance-identifier my-postgres-primary \
    --db-instance-class db.t3.medium \
    --availability-zone us-east-1b

# Cross-region read replica (optional)
aws rds create-db-instance-read-replica \
    --db-instance-identifier my-postgres-replica-west \
    --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:my-postgres-primary \
    --db-instance-class db.t3.medium \
    --region us-west-2
```

## Phase 5: Security Best Practices

### 5.1 Encryption Configuration
- Enable encryption at rest using AWS KMS
- Force SSL connections
- Use IAM database authentication where possible

### 5.2 Network Security
- Deploy RDS in private subnets
- Use security groups with least privilege
- Implement VPC endpoints for additional isolation

### 5.3 Access Control
```sql
-- Create application-specific roles
CREATE ROLE app_read_only;
GRANT CONNECT ON DATABASE myapp TO app_read_only;
GRANT USAGE ON SCHEMA public TO app_read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;

CREATE ROLE app_read_write;
GRANT CONNECT ON DATABASE myapp TO app_read_write;
GRANT USAGE ON SCHEMA public TO app_read_write;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_read_write;
```

## Next Steps
1. Review the migration checklist CSV file
2. Implement the Node.js/TypeScript application
3. Configure monitoring and alerting
4. Plan the production cutover