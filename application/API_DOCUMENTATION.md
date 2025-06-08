# API Documentation

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API does not implement authentication. In production, you should add JWT or OAuth2 authentication.

## Endpoints

### Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "OK",
  "timestamp": "2023-12-07T10:30:00.000Z",
  "database": "Connected",
  "environment": "development"
}
```

### Create User
```
POST /api/users
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "isActive": true
}
```
**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "isActive": true,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:00.000Z"
  }
}
```

### Get Users
```
GET /api/users?isActive=true&limit=10&offset=0&email=john
```
**Query Parameters:**
- `isActive` (boolean, optional): Filter by active status
- `limit` (number, optional): Number of results to return (1-100, default: 50)
- `offset` (number, optional): Number of results to skip (default: 0)
- `email` (string, optional): Search by email (partial match)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "isActive": true,
      "createdAt": "2023-12-07T10:30:00.000Z",
      "updatedAt": "2023-12-07T10:30:00.000Z"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 50,
    "offset": 0,
    "hasMore": false
  }
}
```

### Get User by ID
```
GET /api/users/{id}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "isActive": true,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:00.000Z"
  }
}
```

### Update User
```
PUT /api/users/{id}
```
**Request Body:**
```json
{
  "firstName": "Jane",
  "isActive": false
}
```
**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "isActive": false,
    "createdAt": "2023-12-07T10:30:00.000Z",
    "updatedAt": "2023-12-07T10:30:45.000Z"
  }
}
```

### Delete User
```
DELETE /api/users/{id}
```
**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation error",
  "details": ["email is required", "firstName must be at least 1 character"]
}
```

### Not Found (404)
```json
{
  "success": false,
  "message": "User not found"
}
```

### Conflict (409)
```json
{
  "success": false,
  "message": "Email already exists"
}
```

### Internal Server Error (500)
```json
{
  "success": false,
  "message": "Internal server error"
}
```

## Database Architecture

### Read/Write Separation
- **Write operations** (CREATE, UPDATE, DELETE) use the primary RDS instance
- **Read operations** (SELECT) use read replicas for better performance
- Connection pooling is implemented to manage database connections efficiently

### Performance Optimizations
- Indexes on frequently queried columns
- Connection pooling with configurable pool sizes
- Query timeout settings
- Automatic retry logic for transient errors