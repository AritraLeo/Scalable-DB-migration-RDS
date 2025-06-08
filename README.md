# Supabase to AWS RDS PostgreSQL Migration Project

A comprehensive solution for migrating from Supabase PostgreSQL to AWS RDS with read replicas, featuring a production-ready Node.js/TypeScript application with CRUD operations.

## 📋 Project Overview

This project provides:
- **Complete migration strategy** from Supabase to AWS RDS PostgreSQL
- **Infrastructure as Code** using CloudFormation
- **Production-ready Node.js/TypeScript application** with connection pooling
- **Read/write separation** using RDS read replicas
- **Security best practices** for AWS RDS
- **Comprehensive documentation** and deployment scripts

## 🏗️ Architecture

```
┌─────────────────┐    Migration    ┌─────────────────────────────────────┐
│   Supabase      │ ──────────────► │           AWS Infrastructure        │
│   PostgreSQL    │  pg_dump/restore│                                     │
└─────────────────┘                 │  ┌─────────────┐  ┌─────────────┐   │
                                    │  │   Primary   │  │ Read Replica │   │
┌─────────────────┐                 │  │     RDS     │◄─┤     RDS     │   │
│  Application    │                 │  │ PostgreSQL  │  │ PostgreSQL  │   │
│ Node.js/TypeScript│────────────────┤  └─────────────┘  └─────────────┘   │
│    with CRUD    │   Write/Read    │         │                │           │
└─────────────────┘    Operations   │    Write Ops      Read Ops          │
                                    │                                     │
                                    └─────────────────────────────────────┘
```

## 📁 Project Structure

```
├── README.md                          # This file
├── migration_checklist.csv            # Detailed migration tasks
├── rds-migration-guide.md             # Step-by-step migration guide
├── architecture_diagram.png           # Visual architecture diagram
│
├── infrastructure/
│   ├── cloudformation-template.json   # AWS infrastructure template
│   ├── deploy.sh                     # Deployment script
│   └── schema.sql                    # Database schema
│
├── application/
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── .env.example                  # Environment variables template
│   │
│   ├── src/
│   │   ├── app.ts                    # Main application
│   │   ├── config.ts                 # Configuration management
│   │   ├── logger.ts                 # Logging utility
│   │   ├── database.ts               # Database connection & pooling
│   │   ├── user.types.ts             # TypeScript interfaces
│   │   ├── user.service.ts           # CRUD service layer
│   │   ├── user.controller.ts        # REST API controllers
│   │   └── migrations/
│   │       └── migrate.ts            # Database migration script
│   │
│   └── API_DOCUMENTATION.md          # Complete API documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- AWS CLI configured with appropriate permissions
- PostgreSQL client tools (psql, pg_dump, pg_restore)
- Access to your Supabase database

### 1. Deploy AWS Infrastructure

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy CloudFormation stack
./deploy.sh deploy

# View stack outputs (database endpoints, etc.)
./deploy.sh outputs
```

### 2. Set Up Application

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your RDS endpoints from CloudFormation outputs
# DB_PRIMARY_HOST=your-rds-primary-endpoint.region.rds.amazonaws.com
# DB_REPLICA_HOST=your-rds-replica-endpoint.region.rds.amazonaws.com
```

### 3. Run Database Migration

```bash
# Create database schema
npm run migrate up

# Export from Supabase
pg_dump "postgresql://[user]:[pass]@[supabase-host]:5432/[db]" \
    -Fc -v --schema=public --no-owner --no-acl \
    -f supabase_export.dump

# Import to AWS RDS
pg_restore -v \
    -h [rds-endpoint] -U postgres -d [database] \
    --no-owner --no-acl -j 4 \
    supabase_export.dump
```

### 4. Start Application

```bash
# Development mode
npm run dev

# Production build
npm run build
npm start
```

## 📊 Migration Checklist

The project includes a comprehensive migration checklist (`migration_checklist.csv`) with 18 detailed tasks across 6 phases:

1. **Pre-Migration Planning** (3 tasks)
2. **AWS Infrastructure Setup** (5 tasks)
3. **Database Migration** (3 tasks)
4. **Application Development** (3 tasks)
5. **Testing & Validation** (2 tasks)
6. **Production Cutover** (2 tasks)

## 🔒 Security Features

- **Encryption at rest** using AWS KMS
- **SSL/TLS encryption** in transit
- **VPC isolation** with private subnets
- **Security groups** with least privilege access
- **IAM roles** for enhanced monitoring
- **Parameter groups** for security hardening

## 🔧 Key Features

### Database Layer
- **Connection pooling** with configurable pool sizes
- **Read/write separation** for optimal performance
- **Automatic failover** and retry logic
- **Query timeout protection**
- **Performance monitoring** with CloudWatch

### Application Layer
- **TypeScript** for type safety
- **Express.js** with security middleware
- **Input validation** using Joi
- **Error handling** and logging
- **Health checks** and graceful shutdown
- **CORS and compression** support

### API Features
- **RESTful endpoints** for all CRUD operations
- **Pagination** support
- **Filtering and search** capabilities
- **Comprehensive error responses**
- **API documentation** with examples

## 🛠️ Available Scripts

```bash
# Development
npm run dev          # Start development server with hot reload
npm run build        # Build TypeScript to JavaScript
npm start           # Start production server

# Database
npm run migrate up   # Run database migrations
npm run migrate down # Rollback database migrations

# Testing
npm test            # Run test suite (when implemented)
```

## 📖 API Documentation

The application provides a comprehensive REST API for user management:

### Endpoints
- `POST /api/users` - Create user
- `GET /api/users` - List users with filtering
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user
- `GET /health` - Health check

See `API_DOCUMENTATION.md` for complete details with examples.

## 🔍 Monitoring and Performance

### CloudWatch Metrics
- Database CPU, memory, and disk usage
- Connection count and query performance
- Read/write operation metrics
- Replication lag monitoring

### Application Monitoring
- Request/response times
- Error rates and patterns
- Database connection pool status
- Custom business metrics

## 🎯 Performance Optimizations

### Database Level
- **Indexes** on frequently queried columns
- **Connection pooling** to reduce overhead
- **Read replicas** for read scaling
- **Parameter tuning** for AWS RDS
- **Query optimization** with explain plans

### Application Level
- **Efficient SQL queries** with proper indexing
- **Connection reuse** through pooling
- **Caching strategies** for frequently accessed data
- **Compression** for HTTP responses
- **Request validation** to prevent invalid queries

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check security group rules
   - Verify network connectivity
   - Review connection pool settings

2. **Migration Failures**
   - Validate source data integrity
   - Check target database permissions
   - Review pg_dump/pg_restore logs

3. **Performance Issues**
   - Monitor CloudWatch metrics
   - Review slow query logs
   - Optimize database indexes

### Health Checks

```bash
# Application health
curl http://localhost:3000/health

# Database connectivity
psql -h [rds-endpoint] -U postgres -d [database] -c "SELECT NOW();"
```

## 📈 Scaling Considerations

### Vertical Scaling
- Increase RDS instance class
- Adjust connection pool sizes
- Optimize memory settings

### Horizontal Scaling
- Add more read replicas
- Implement application-level caching
- Use load balancers for application tier

## 🔄 Maintenance

### Regular Tasks
- Monitor CloudWatch alarms
- Review RDS maintenance windows
- Update application dependencies
- Backup verification

### Updates
- Database parameter tuning
- Application security patches
- Infrastructure updates via CloudFormation

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs and metrics
3. Consult AWS RDS documentation
4. Check application logs for detailed error information

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: Remember to customize the configuration files, security settings, and monitoring setup according to your specific requirements and security policies.