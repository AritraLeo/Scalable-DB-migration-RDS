-- AWS RDS PostgreSQL Database Schema
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
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;