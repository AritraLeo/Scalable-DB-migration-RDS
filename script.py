# Create Node.js/TypeScript project structure with all necessary files

# Package.json
package_json = """{
  "name": "postgres-rds-crud-app",
  "version": "1.0.0",
  "description": "Node.js TypeScript CRUD application for AWS RDS PostgreSQL with read replicas",
  "main": "dist/app.js",
  "scripts": {
    "start": "node dist/app.js",
    "dev": "nodemon --exec ts-node src/app.ts",
    "build": "tsc",
    "test": "jest",
    "migrate": "ts-node src/migrations/migrate.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.3",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "dotenv": "^16.3.1",
    "joi": "^17.9.2",
    "compression": "^1.7.4"
  },
  "devDependencies": {
    "@types/node": "^20.5.0",
    "@types/express": "^4.17.17",
    "@types/pg": "^8.10.2",
    "@types/cors": "^2.8.13",
    "@types/compression": "^1.7.2",
    "@types/jest": "^29.5.3",
    "typescript": "^5.1.6",
    "ts-node": "^10.9.1",
    "nodemon": "^3.0.1",
    "jest": "^29.6.1",
    "ts-jest": "^29.1.1"
  },
  "keywords": ["postgresql", "aws-rds", "typescript", "crud", "read-replicas"],
  "author": "Your Name",
  "license": "MIT"
}"""

with open('package.json', 'w') as f:
    f.write(package_json)

# TypeScript configuration
tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitThis": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts"
  ]
}"""

with open('tsconfig.json', 'w') as f:
    f.write(tsconfig)

# Environment configuration
env_example = """# Database Configuration
DB_PRIMARY_HOST=your-rds-primary-endpoint.region.rds.amazonaws.com
DB_REPLICA_HOST=your-rds-replica-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USERNAME=postgres
DB_PASSWORD=your_secure_password

# Connection Pool Settings
DB_POOL_MIN=2
DB_POOL_MAX=20
DB_POOL_IDLE_TIMEOUT=10000
DB_POOL_CONNECTION_TIMEOUT=5000

# Application Settings
PORT=3000
NODE_ENV=development

# SSL Configuration (for production)
DB_SSL=true
DB_SSL_REJECT_UNAUTHORIZED=false

# Monitoring and Logging
LOG_LEVEL=info
ENABLE_QUERY_LOGGING=false"""

with open('.env.example', 'w') as f:
    f.write(env_example)

print("Project structure files created successfully!")
print("Files created:")
print("- package.json")
print("- tsconfig.json") 
print("- .env.example")