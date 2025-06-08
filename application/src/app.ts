import express, { Application, Request, Response, NextFunction } from 'express';
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

export default app;