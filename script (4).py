# Create REST API controller and main application

# User controller with REST endpoints
user_controller = """import { Request, Response, NextFunction } from 'express';
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
}"""

with open('user.controller.ts', 'w') as f:
    f.write(user_controller)

# Main application file
app_file = """import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { config } from './config';
import { logger } from './logger';
import { dbManager } from './database';
import { UserController } from './user.controller';

class App {
  private app: Application;
  private userController: UserController;

  constructor() {
    this.app = express();
    this.userController = new UserController();
    this.initializeMiddleware();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private initializeMiddleware(): void {
    // Security middleware
    this.app.use(helmet());
    
    // CORS configuration
    this.app.use(cors({
      origin: config.app.env === 'production' ? ['your-frontend-domain.com'] : true,
      credentials: true
    }));

    // Compression middleware
    this.app.use(compression());

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging middleware
    this.app.use((req: Request, res: Response, next: NextFunction) => {
      logger.info(`${req.method} ${req.path} - ${req.ip}`);
      next();
    });
  }

  private initializeRoutes(): void {
    // Health check endpoint
    this.app.get('/health', async (req: Request, res: Response) => {
      try {
        const dbHealthy = await dbManager.testConnections();
        
        res.json({
          status: 'OK',
          timestamp: new Date().toISOString(),
          database: dbHealthy ? 'Connected' : 'Disconnected',
          environment: config.app.env
        });
      } catch (error) {
        logger.error('Health check failed:', error);
        res.status(503).json({
          status: 'ERROR',
          timestamp: new Date().toISOString(),
          database: 'Disconnected',
          environment: config.app.env
        });
      }
    });

    // API routes
    const apiRouter = express.Router();
    
    // User routes
    apiRouter.post('/users', this.userController.createUser);
    apiRouter.get('/users', this.userController.getUsers);
    apiRouter.get('/users/:id', this.userController.getUserById);
    apiRouter.put('/users/:id', this.userController.updateUser);
    apiRouter.delete('/users/:id', this.userController.deleteUser);

    this.app.use('/api', apiRouter);

    // Root endpoint
    this.app.get('/', (req: Request, res: Response) => {
      res.json({
        message: 'AWS RDS PostgreSQL CRUD API',
        version: '1.0.0',
        documentation: '/api-docs',
        health: '/health'
      });
    });

    // 404 handler
    this.app.use('*', (req: Request, res: Response) => {
      res.status(404).json({
        success: false,
        message: 'Route not found'
      });
    });
  }

  private initializeErrorHandling(): void {
    // Global error handler
    this.app.use((error: Error, req: Request, res: Response, next: NextFunction) => {
      logger.error('Unhandled error:', error);

      // Don't leak error details in production
      const message = config.app.env === 'production' 
        ? 'Internal server error' 
        : error.message;

      res.status(500).json({
        success: false,
        message,
        ...(config.app.env !== 'production' && { stack: error.stack })
      });
    });

    // Handle uncaught exceptions
    process.on('uncaughtException', (error: Error) => {
      logger.error('Uncaught exception:', error);
      this.gracefulShutdown();
    });

    // Handle unhandled promise rejections
    process.on('unhandledRejection', (reason: any) => {
      logger.error('Unhandled rejection:', reason);
      this.gracefulShutdown();
    });

    // Handle termination signals
    process.on('SIGTERM', () => {
      logger.info('SIGTERM received, shutting down gracefully');
      this.gracefulShutdown();
    });

    process.on('SIGINT', () => {
      logger.info('SIGINT received, shutting down gracefully');
      this.gracefulShutdown();
    });
  }

  private async gracefulShutdown(): Promise<void> {
    logger.info('Starting graceful shutdown...');
    
    try {
      await dbManager.gracefulShutdown();
      logger.info('Graceful shutdown completed');
      process.exit(0);
    } catch (error) {
      logger.error('Error during graceful shutdown:', error);
      process.exit(1);
    }
  }

  public async start(): Promise<void> {
    try {
      // Test database connections before starting server
      const dbHealthy = await dbManager.testConnections();
      if (!dbHealthy) {
        throw new Error('Database connection failed');
      }

      // Start server
      this.app.listen(config.app.port, () => {
        logger.info(`Server started on port ${config.app.port}`);
        logger.info(`Environment: ${config.app.env}`);
        logger.info(`Health check: http://localhost:${config.app.port}/health`);
      });
    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  public getApp(): Application {
    return this.app;
  }
}

// Start application
const app = new App();
app.start().catch((error) => {
  logger.error('Application startup failed:', error);
  process.exit(1);
});

export default app;"""

with open('app.ts', 'w') as f:
    f.write(app_file)

print("REST API and application files created successfully!")
print("Files created:")
print("- user.controller.ts (REST API controller with validation)")
print("- app.ts (Main Express application with middleware and error handling)")