import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { UserService } from './user.service';
import { CreateUserRequest, UpdateUserRequest, UserFilters } from './user.types';
import { logger } from './logger';

export class UserController {
  private userService: UserService;

  constructor() {
    this.userService = new UserService();
  }

  // Validation schemas
  private createUserSchema = Joi.object({
    email: Joi.string().email().required(),
    firstName: Joi.string().min(1).max(100).required(),
    lastName: Joi.string().min(1).max(100).required(),
    isActive: Joi.boolean().optional()
  });

  private updateUserSchema = Joi.object({
    email: Joi.string().email().optional(),
    firstName: Joi.string().min(1).max(100).optional(),
    lastName: Joi.string().min(1).max(100).optional(),
    isActive: Joi.boolean().optional()
  }).min(1);

  /**
   * Create a new user
   * POST /api/users
   */
  createUser = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // Validate request body
      const { error, value } = this.createUserSchema.validate(req.body);
      if (error) {
        res.status(400).json({
          success: false,
          message: 'Validation error',
          details: error.details.map(d => d.message)
        });
        return;
      }

      const userData: CreateUserRequest = value;

      // Check if email already exists
      const emailExists = await this.userService.emailExists(userData.email);
      if (emailExists) {
        res.status(409).json({
          success: false,
          message: 'Email already exists'
        });
        return;
      }

      // Create user
      const user = await this.userService.createUser(userData);

      res.status(201).json({
        success: true,
        message: 'User created successfully',
        data: user
      });
    } catch (error) {
      logger.error('Error in createUser controller:', error);
      next(error);
    }
  };

  /**
   * Get user by ID
   * GET /api/users/:id
   */
  getUserById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { id } = req.params;

      if (!id) {
        res.status(400).json({
          success: false,
          message: 'User ID is required'
        });
        return;
      }

      const user = await this.userService.getUserById(id);

      if (!user) {
        res.status(404).json({
          success: false,
          message: 'User not found'
        });
        return;
      }

      res.json({
        success: true,
        data: user
      });
    } catch (error) {
      logger.error('Error in getUserById controller:', error);
      next(error);
    }
  };

  /**
   * Get users with optional filters
   * GET /api/users
   */
  getUsers = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const filters: UserFilters = {
        isActive: req.query.isActive === 'true' ? true : req.query.isActive === 'false' ? false : undefined,
        email: req.query.email as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      };

      // Validate pagination parameters
      if (filters.limit && (filters.limit < 1 || filters.limit > 100)) {
        res.status(400).json({
          success: false,
          message: 'Limit must be between 1 and 100'
        });
        return;
      }

      if (filters.offset && filters.offset < 0) {
        res.status(400).json({
          success: false,
          message: 'Offset must be non-negative'
        });
        return;
      }

      const result = await this.userService.getUsers(filters);

      res.json({
        success: true,
        data: result.users,
        pagination: {
          total: result.total,
          limit: filters.limit || 50,
          offset: filters.offset || 0,
          hasMore: (filters.offset || 0) + (filters.limit || 50) < result.total
        }
      });
    } catch (error) {
      logger.error('Error in getUsers controller:', error);
      next(error);
    }
  };

  /**
   * Update user
   * PUT /api/users/:id
   */
  updateUser = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { id } = req.params;

      if (!id) {
        res.status(400).json({
          success: false,
          message: 'User ID is required'
        });
        return;
      }

      // Validate request body
      const { error, value } = this.updateUserSchema.validate(req.body);
      if (error) {
        res.status(400).json({
          success: false,
          message: 'Validation error',
          details: error.details.map(d => d.message)
        });
        return;
      }

      const userData: UpdateUserRequest = value;

      // Check if email already exists (excluding current user)
      if (userData.email) {
        const emailExists = await this.userService.emailExists(userData.email, id);
        if (emailExists) {
          res.status(409).json({
            success: false,
            message: 'Email already exists'
          });
          return;
        }
      }

      const updatedUser = await this.userService.updateUser(id, userData);

      if (!updatedUser) {
        res.status(404).json({
          success: false,
          message: 'User not found'
        });
        return;
      }

      res.json({
        success: true,
        message: 'User updated successfully',
        data: updatedUser
      });
    } catch (error) {
      logger.error('Error in updateUser controller:', error);
      next(error);
    }
  };

  /**
   * Delete user
   * DELETE /api/users/:id
   */
  deleteUser = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { id } = req.params;

      if (!id) {
        res.status(400).json({
          success: false,
          message: 'User ID is required'
        });
        return;
      }

      const deleted = await this.userService.deleteUser(id);

      if (!deleted) {
        res.status(404).json({
          success: false,
          message: 'User not found'
        });
        return;
      }

      res.json({
        success: true,
        message: 'User deleted successfully'
      });
    } catch (error) {
      logger.error('Error in deleteUser controller:', error);
      next(error);
    }
  };
}