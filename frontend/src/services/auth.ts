import { apiClient } from './api';
import type { LoginCredentials, RegisterData, User } from '../types';

export class AuthService {
  async login(credentials: LoginCredentials) {
    // FastAPI expects form data for OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

    try {
      const response = await fetch(`${baseURL}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      return {
        user: data.user,
        token: data.access_token
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async register(userData: RegisterData) {
    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

    try {
      const response = await fetch(`${baseURL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          first_name: userData.firstName,
          last_name: userData.lastName,
          role: userData.role || 'PATIENT'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      await response.json(); // Registration successful

      // After successful registration, automatically login
      return await this.login({ email: userData.email, password: userData.password });

    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout() {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
  }

  async refreshToken() {
    const response = await apiClient.post<{ token: string }>('/auth/refresh');

    if (response.success && response.data) {
      localStorage.setItem('auth_token', response.data.token);
      return response.data.token;
    }

    throw new Error('Token refresh failed');
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    const token = this.getAuthToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  async updateProfile(userData: Partial<User>) {
    const response = await apiClient.put<User>('/auth/profile', userData);

    if (response.success && response.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    }

    throw new Error(response.message || 'Profile update failed');
  }

  async changePassword(currentPassword: string, newPassword: string) {
    const response = await apiClient.post('/auth/change-password', {
      currentPassword,
      newPassword,
    });

    if (!response.success) {
      throw new Error(response.message || 'Password change failed');
    }

    return response;
  }
}

export const authService = new AuthService();