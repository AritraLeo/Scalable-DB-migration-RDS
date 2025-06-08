import { Pool } from 'pg';
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
}