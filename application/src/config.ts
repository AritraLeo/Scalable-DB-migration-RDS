import dotenv from 'dotenv';

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
}