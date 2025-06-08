import { Pool, PoolConfig } from 'pg';
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
};