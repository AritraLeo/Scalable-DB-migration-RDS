# Create the core TypeScript application files

# Database configuration and connection pooling
database_config = """import { Pool, PoolConfig } from 'pg';
import { config } from './config';
import { logger } from './logger';

export interface DatabaseConnection {
  primary: Pool;
  replica: Pool;
}

class DatabaseManager {
  private static instance: DatabaseManager;
  private primaryPool: Pool;
  private replicaPool: Pool;

  private constructor() {
    this.primaryPool = this.createPool(config.database.primary);
    this.replicaPool = this.createPool(config.database.replica);
    this.setupErrorHandlers();
  }

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  private createPool(dbConfig: PoolConfig): Pool {
    const pool = new Pool({
      host: dbConfig.host,
      port: dbConfig.port,
      database: dbConfig.database,
      user: dbConfig.user,
      password: dbConfig.password,
      ssl: config.database.ssl,
      min: config.database.pool.min,
      max: config.database.pool.max,
      idleTimeoutMillis: config.database.pool.idleTimeout,
      connectionTimeoutMillis: config.database.pool.connectionTimeout,
      statement_timeout: 30000,
      query_timeout: 30000,
      application_name: 'rds-crud-app'
    });

    return pool;
  }

  private setupErrorHandlers(): void {
    this.primaryPool.on('error', (err) => {
      logger.error('Primary database pool error:', err);
    });

    this.replicaPool.on('error', (err) => {
      logger.error('Replica database pool error:', err);
    });

    this.primaryPool.on('connect', () => {
      logger.info('New client connected to primary database');
    });

    this.replicaPool.on('connect', () => {
      logger.info('New client connected to replica database');
    });
  }

  public getPrimaryPool(): Pool {
    return this.primaryPool;
  }

  public getReplicaPool(): Pool {
    return this.replicaPool;
  }

  public async testConnections(): Promise<boolean> {
    try {
      const primaryTest = await this.primaryPool.query('SELECT NOW() as primary_time');
      const replicaTest = await this.replicaPool.query('SELECT NOW() as replica_time');
      
      logger.info('Database connections tested successfully');
      logger.info(`Primary DB time: ${primaryTest.rows[0].primary_time}`);
      logger.info(`Replica DB time: ${replicaTest.rows[0].replica_time}`);
      
      return true;
    } catch (error) {
      logger.error('Database connection test failed:', error);
      return false;
    }
  }

  public async gracefulShutdown(): Promise<void> {
    logger.info('Closing database connections...');
    await Promise.all([
      this.primaryPool.end(),
      this.replicaPool.end()
    ]);
    logger.info('Database connections closed');
  }
}

export const dbManager = DatabaseManager.getInstance();
export const db = {
  primary: dbManager.getPrimaryPool(),
  replica: dbManager.getReplicaPool()
};"""

with open('database.ts', 'w') as f:
    f.write(database_config)

# Configuration management
config_file = """import dotenv from 'dotenv';

dotenv.config();

export const config = {
  app: {
    port: parseInt(process.env.PORT || '3000', 10),
    env: process.env.NODE_ENV || 'development',
    logLevel: process.env.LOG_LEVEL || 'info'
  },
  database: {
    primary: {
      host: process.env.DB_PRIMARY_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432', 10),
      database: process.env.DB_NAME || 'postgres',
      user: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'password'
    },
    replica: {
      host: process.env.DB_REPLICA_HOST || process.env.DB_PRIMARY_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432', 10),
      database: process.env.DB_NAME || 'postgres',
      user: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'password'
    },
    ssl: process.env.DB_SSL === 'true' ? {
      rejectUnauthorized: process.env.DB_SSL_REJECT_UNAUTHORIZED !== 'false'
    } : false,
    pool: {
      min: parseInt(process.env.DB_POOL_MIN || '2', 10),
      max: parseInt(process.env.DB_POOL_MAX || '20', 10),
      idleTimeout: parseInt(process.env.DB_POOL_IDLE_TIMEOUT || '10000', 10),
      connectionTimeout: parseInt(process.env.DB_POOL_CONNECTION_TIMEOUT || '5000', 10)
    },
    enableQueryLogging: process.env.ENABLE_QUERY_LOGGING === 'true'
  }
};

// Validate required environment variables
const requiredEnvVars = [
  'DB_PRIMARY_HOST',
  'DB_NAME',
  'DB_USERNAME',
  'DB_PASSWORD'
];

const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0) {
  throw new Error(`Missing required environment variables: ${missingEnvVars.join(', ')}`);
}"""

with open('config.ts', 'w') as f:
    f.write(config_file)

# Logger utility
logger_file = """import { config } from './config';

export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3
}

class Logger {
  private logLevel: LogLevel;

  constructor() {
    this.logLevel = this.parseLogLevel(config.app.logLevel);
  }

  private parseLogLevel(level: string): LogLevel {
    switch (level.toLowerCase()) {
      case 'error': return LogLevel.ERROR;
      case 'warn': return LogLevel.WARN;
      case 'info': return LogLevel.INFO;
      case 'debug': return LogLevel.DEBUG;
      default: return LogLevel.INFO;
    }
  }

  private log(level: LogLevel, message: string, ...args: any[]): void {
    if (level <= this.logLevel) {
      const timestamp = new Date().toISOString();
      const levelName = LogLevel[level];
      console.log(`[${timestamp}] [${levelName}] ${message}`, ...args);
    }
  }

  error(message: string, ...args: any[]): void {
    this.log(LogLevel.ERROR, message, ...args);
  }

  warn(message: string, ...args: any[]): void {
    this.log(LogLevel.WARN, message, ...args);
  }

  info(message: string, ...args: any[]): void {
    this.log(LogLevel.INFO, message, ...args);
  }

  debug(message: string, ...args: any[]): void {
    this.log(LogLevel.DEBUG, message, ...args);
  }
}

export const logger = new Logger();"""

with open('logger.ts', 'w') as f:
    f.write(logger_file)

print("Core application files created successfully!")
print("Files created:")
print("- database.ts (Database configuration and pooling)")
print("- config.ts (Configuration management)")
print("- logger.ts (Logging utility)")