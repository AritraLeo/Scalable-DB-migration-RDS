export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateUserRequest {
  email: string;
  firstName: string;
  lastName: string;
  isActive?: boolean;
}

export interface UpdateUserRequest {
  email?: string;
  firstName?: string;
  lastName?: string;
  isActive?: boolean;
}

export interface UserFilters {
  isActive?: boolean;
  email?: string;
  limit?: number;
  offset?: number;
}