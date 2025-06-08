import { Pool, QueryResult } from 'pg';
import { db } from './database';
import { logger } from './logger';
import { User, CreateUserRequest, UpdateUserRequest, UserFilters } from './user.types';

export class UserService {
  private primaryDb: Pool;
  private replicaDb: Pool;

  constructor() {
    this.primaryDb = db.primary;
    this.replicaDb = db.replica;
  }

  /**
   * Create a new user (Write operation - uses primary DB)
   */
  async createUser(userData: CreateUserRequest): Promise<User> {
    const query = `
      INSERT INTO users (email, first_name, last_name, is_active, created_at, updated_at)
      VALUES ($1, $2, $3, $4, NOW(), NOW())
      RETURNING id, email, first_name as "firstName", last_name as "lastName", 
                is_active as "isActive", created_at as "createdAt", updated_at as "updatedAt"
    `;

    const values = [
      userData.email,
      userData.firstName,
      userData.lastName,
      userData.isActive ?? true
    ];

    try {
      logger.info(`Creating user with email: ${userData.email}`);
      const result: QueryResult<User> = await this.primaryDb.query(query, values);
      logger.info(`User created successfully with ID: ${result.rows[0].id}`);
      return result.rows[0];
    } catch (error) {
      logger.error('Error creating user:', error);
      throw new Error(`Failed to create user: ${error}`);
    }
  }

  /**
   * Get user by ID (Read operation - uses replica DB for better performance)
   */
  async getUserById(id: string): Promise<User | null> {
    const query = `
      SELECT id, email, first_name as "firstName", last_name as "lastName",
             is_active as "isActive", created_at as "createdAt", updated_at as "updatedAt"
      FROM users 
      WHERE id = $1
    `;

    try {
      logger.debug(`Fetching user with ID: ${id}`);
      const result: QueryResult<User> = await this.replicaDb.query(query, [id]);

      if (result.rows.length === 0) {
        logger.info(`User not found with ID: ${id}`);
        return null;
      }

      logger.debug(`User found: ${result.rows[0].email}`);
      return result.rows[0];
    } catch (error) {
      logger.error('Error fetching user by ID:', error);
      throw new Error(`Failed to fetch user: ${error}`);
    }
  }

  /**
   * Get users with filters (Read operation - uses replica DB)
   */
  async getUsers(filters: UserFilters = {}): Promise<{ users: User[]; total: number }> {
    let whereClause = 'WHERE 1=1';
    const values: any[] = [];
    let paramIndex = 1;

    // Build dynamic WHERE clause
    if (filters.isActive !== undefined) {
      whereClause += ` AND is_active = $${paramIndex}`;
      values.push(filters.isActive);
      paramIndex++;
    }

    if (filters.email) {
      whereClause += ` AND email ILIKE $${paramIndex}`;
      values.push(`%${filters.email}%`);
      paramIndex++;
    }

    // Count query
    const countQuery = `SELECT COUNT(*) as total FROM users ${whereClause}`;

    // Main query with pagination
    const limit = filters.limit || 50;
    const offset = filters.offset || 0;

    const mainQuery = `
      SELECT id, email, first_name as "firstName", last_name as "lastName",
             is_active as "isActive", created_at as "createdAt", updated_at as "updatedAt"
      FROM users 
      ${whereClause}
      ORDER BY created_at DESC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    values.push(limit, offset);

    try {
      logger.debug('Fetching users with filters:', filters);

      const [countResult, usersResult] = await Promise.all([
        this.replicaDb.query(countQuery, values.slice(0, paramIndex - 1)),
        this.replicaDb.query(mainQuery, values)
      ]);

      const total = parseInt(countResult.rows[0].total, 10);
      const users = usersResult.rows;

      logger.info(`Fetched ${users.length} users out of ${total} total`);

      return { users, total };
    } catch (error) {
      logger.error('Error fetching users:', error);
      throw new Error(`Failed to fetch users: ${error}`);
    }
  }

  /**
   * Update user (Write operation - uses primary DB)
   */
  async updateUser(id: string, userData: UpdateUserRequest): Promise<User | null> {
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    // Build dynamic SET clause
    if (userData.email !== undefined) {
      updates.push(`email = $${paramIndex}`);
      values.push(userData.email);
      paramIndex++;
    }

    if (userData.firstName !== undefined) {
      updates.push(`first_name = $${paramIndex}`);
      values.push(userData.firstName);
      paramIndex++;
    }

    if (userData.lastName !== undefined) {
      updates.push(`last_name = $${paramIndex}`);
      values.push(userData.lastName);
      paramIndex++;
    }

    if (userData.isActive !== undefined) {
      updates.push(`is_active = $${paramIndex}`);
      values.push(userData.isActive);
      paramIndex++;
    }

    if (updates.length === 0) {
      throw new Error('No fields to update');
    }

    updates.push(`updated_at = NOW()`);
    values.push(id);

    const query = `
      UPDATE users 
      SET ${updates.join(', ')}
      WHERE id = $${paramIndex}
      RETURNING id, email, first_name as "firstName", last_name as "lastName",
                is_active as "isActive", created_at as "createdAt", updated_at as "updatedAt"
    `;

    try {
      logger.info(`Updating user with ID: ${id}`);
      const result: QueryResult<User> = await this.primaryDb.query(query, values);

      if (result.rows.length === 0) {
        logger.info(`User not found for update with ID: ${id}`);
        return null;
      }

      logger.info(`User updated successfully: ${result.rows[0].email}`);
      return result.rows[0];
    } catch (error) {
      logger.error('Error updating user:', error);
      throw new Error(`Failed to update user: ${error}`);
    }
  }

  /**
   * Delete user (Write operation - uses primary DB)
   */
  async deleteUser(id: string): Promise<boolean> {
    const query = 'DELETE FROM users WHERE id = $1';

    try {
      logger.info(`Deleting user with ID: ${id}`);
      const result = await this.primaryDb.query(query, [id]);

      const deleted = result.rowCount > 0;
      if (deleted) {
        logger.info(`User deleted successfully with ID: ${id}`);
      } else {
        logger.info(`User not found for deletion with ID: ${id}`);
      }

      return deleted;
    } catch (error) {
      logger.error('Error deleting user:', error);
      throw new Error(`Failed to delete user: ${error}`);
    }
  }

  /**
   * Check if email exists (Read operation - uses replica DB)
   */
  async emailExists(email: string, excludeId?: string): Promise<boolean> {
    let query = 'SELECT 1 FROM users WHERE email = $1';
    const values: any[] = [email];

    if (excludeId) {
      query += ' AND id != $2';
      values.push(excludeId);
    }

    try {
      const result = await this.replicaDb.query(query, values);
      return result.rows.length > 0;
    } catch (error) {
      logger.error('Error checking email existence:', error);
      throw new Error(`Failed to check email existence: ${error}`);
    }
  }
}