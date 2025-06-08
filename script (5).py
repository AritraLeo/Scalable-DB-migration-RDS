# Create database schema and migration files

# Database schema SQL
schema_sql = """-- AWS RDS PostgreSQL Database Schema
-- Optimized for performance with proper indexing

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_full_name ON users(first_name, last_name);

-- Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_users_active_created ON users(is_active, created_at DESC);

-- Create trigger function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create sample data for testing (optional)
INSERT INTO users (email, first_name, last_name, is_active) VALUES
    ('john.doe@example.com', 'John', 'Doe', true),
    ('jane.smith@example.com', 'Jane', 'Smith', true),
    ('bob.johnson@example.com', 'Bob', 'Johnson', false),
    ('alice.williams@example.com', 'Alice', 'Williams', true)
ON CONFLICT (email) DO NOTHING;

-- Performance optimization settings for AWS RDS
-- These should be set in your RDS parameter group

-- Example parameter group settings:
-- shared_preload_libraries = 'pg_stat_statements'
-- log_statement = 'all'  -- For development only, remove in production
-- log_min_duration_statement = 1000  -- Log queries taking more than 1 second
-- effective_cache_size = '75% of instance memory'
-- shared_buffers = '25% of instance memory'
-- work_mem = '4MB'
-- maintenance_work_mem = '64MB'
-- checkpoint_completion_target = 0.9
-- wal_buffers = '16MB'
-- random_page_cost = 1.1  -- For SSD storage

-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Grant permissions for application user
-- Run these commands with your application database user
-- GRANT CONNECT ON DATABASE your_database_name TO app_user;
-- GRANT USAGE ON SCHEMA public TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;"""

with open('schema.sql', 'w') as f:
    f.write(schema_sql)

# Migration script
migration_script = """import { Pool } from 'pg';
import { readFileSync } from 'fs';
import { join } from 'path';
import { config } from '../config';
import { logger } from '../logger';

class DatabaseMigrator {
  private pool: Pool;

  constructor() {
    this.pool = new Pool({
      host: config.database.primary.host,
      port: config.database.primary.port,
      database: config.database.primary.database,
      user: config.database.primary.user,
      password: config.database.primary.password,
      ssl: config.database.ssl
    });
  }

  async runMigrations(): Promise<void> {
    try {
      logger.info('Starting database migrations...');

      // Read and execute schema.sql
      const schemaPath = join(__dirname, '../../schema.sql');
      const schemaSql = readFileSync(schemaPath, 'utf8');

      await this.pool.query(schemaSql);
      logger.info('Schema migration completed successfully');

      // Verify table creation
      const tableCheck = await this.pool.query(`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
      `);

      if (tableCheck.rows.length === 0) {
        throw new Error('Users table was not created');
      }

      logger.info('Database migration verification passed');

    } catch (error) {
      logger.error('Migration failed:', error);
      throw error;
    } finally {
      await this.pool.end();
    }
  }

  async rollback(): Promise<void> {
    try {
      logger.warn('Starting database rollback...');

      // Drop tables in reverse order
      await this.pool.query('DROP TABLE IF EXISTS users CASCADE;');
      await this.pool.query('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;');

      logger.info('Database rollback completed');

    } catch (error) {
      logger.error('Rollback failed:', error);
      throw error;
    } finally {
      await this.pool.end();
    }
  }
}

// CLI interface
const command = process.argv[2];
const migrator = new DatabaseMigrator();

switch (command) {
  case 'up':
    migrator.runMigrations()
      .then(() => {
        logger.info('Migration completed successfully');
        process.exit(0);
      })
      .catch((error) => {
        logger.error('Migration failed:', error);
        process.exit(1);
      });
    break;

  case 'down':
    migrator.rollback()
      .then(() => {
        logger.info('Rollback completed successfully');
        process.exit(0);
      })
      .catch((error) => {
        logger.error('Rollback failed:', error);
        process.exit(1);
      });
    break;

  default:
    logger.info('Usage: ts-node src/migrations/migrate.ts [up|down]');
    process.exit(1);
}"""

with open('migrate.ts', 'w') as f:
    f.write(migration_script)

# API documentation
api_docs = """# API Documentation

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API does not implement authentication. In production, you should add JWT or OAuth2 authentication.

## Endpoints

### Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "OK",
  "timestamp": "2023-12-07T10:30:00.000Z",
  "database": "Connected",
  "environment": "development"
}
```

### Create User
```
POST /api/users
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "isActive": true
}
```
**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "isActive": true,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:00.000Z"
  }
}
```

### Get Users
```
GET /api/users?isActive=true&limit=10&offset=0&email=john
```
**Query Parameters:**
- `isActive` (boolean, optional): Filter by active status
- `limit` (number, optional): Number of results to return (1-100, default: 50)
- `offset` (number, optional): Number of results to skip (default: 0)
- `email` (string, optional): Search by email (partial match)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "isActive": true,
      "createdAt": "2023-12-07T10:30:00.000Z",
      "updatedAt": "2023-12-07T10:30:00.000Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 50,
    "offset": 0,
    "hasMore": false
  }
}
```

### Get User by ID
```
GET /api/users/{id}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "isActive": true,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:00.000Z"
  }
}
```

### Update User
```
PUT /api/users/{id}
```
**Request Body:**
```json
{
  "firstName": "Jane",
  "isActive": false
}
```
**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "isActive": false,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:45.000Z"
  }
}
```

### Delete User
```
DELETE /api/users/{id}
```
**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation error",
  "details": ["email is required", "firstName must be at least 1 character"]
}
```

### Not Found (404)
```json
{
  "success": false,
  "message": "User not found"
}
```

### Conflict (409)
```json
{
  "success": false,
  "message": "Email already exists"
}
```

### Internal Server Error (500)
```json
{
  "success": false,
  "message": "Internal server error"
}
```

## Database Architecture

### Read/Write Separation
- **Write operations** (CREATE, UPDATE, DELETE) use the primary RDS instance
- **Read operations** (SELECT) use read replicas for better performance
- Connection pooling is implemented to manage database connections efficiently

### Performance Optimizations
- Indexes on frequently queried columns
- Connection pooling with configurable pool sizes
- Query timeout settings
- Automatic retry logic for transient errors"""

with open('API_DOCUMENTATION.md', 'w') as f:
    f.write(api_docs)

print("Database and documentation files created successfully!")
print("Files created:")
print("- schema.sql (Database schema with optimizations)")
print("- migrate.ts (Database migration script)")
print("- API_DOCUMENTATION.md (Complete API documentation)")