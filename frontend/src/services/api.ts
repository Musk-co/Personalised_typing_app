/**
 * API client for backend communication
 */

import axios, { AxiosInstance } from 'axios'
import { User, TypingSession, UserStats, AdapterRecommendation, AuthResponse } from '@types/index'
import { SessionCreateRequest, SessionUpdateRequest } from '@types/api'

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to requests if available
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle 401 responses
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // ============ Auth Endpoints ============
  async register(email: string, username: string, password: string, fullName?: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', {
      email,
      username,
      password,
      full_name: fullName,
    })
    return response.data
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', {
      email,
      password,
    })
    return response.data
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout')
  }

  // ============ Session Endpoints ============
  async createSession(data: SessionCreateRequest): Promise<TypingSession> {
    const response = await this.client.post<TypingSession>('/sessions', data)
    return response.data
  }

  async getSession(sessionId: number): Promise<TypingSession> {
    const response = await this.client.get<TypingSession>(`/sessions/${sessionId}`)
    return response.data
  }

  async listSessions(skip: number = 0, limit: number = 20): Promise<TypingSession[]> {
    const response = await this.client.get<TypingSession[]>('/sessions', {
      params: { skip, limit },
    })
    return response.data
  }

  async updateSession(sessionId: number, data: SessionUpdateRequest): Promise<TypingSession> {
    const response = await this.client.put<TypingSession>(`/sessions/${sessionId}`, data)
    return response.data
  }

  // ============ User Endpoints ============
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/users/me')
    return response.data
  }

  async getUser(userId: number): Promise<User> {
    const response = await this.client.get<User>(`/users/${userId}`)
    return response.data
  }

  async updateProfile(data: Record<string, unknown>): Promise<User> {
    const response = await this.client.put<User>('/users/me', data)
    return response.data
  }

  async getPreferences(): Promise<Record<string, unknown>> {
    const response = await this.client.get('/users/preferences')
    return response.data
  }

  async setPreferences(preferences: Record<string, unknown>): Promise<Record<string, unknown>> {
    const response = await this.client.post('/users/preferences', preferences)
    return response.data
  }

  // ============ Analytics Endpoints ============
  async getUserStats(days: number = 30): Promise<UserStats> {
    const response = await this.client.get<UserStats>('/analytics/stats', {
      params: { days },
    })
    return response.data
  }

  async getProgressData(days: number = 30): Promise<Array<{ date: string; wpm: number; accuracy: number }>> {
    const response = await this.client.get('/analytics/progress', {
      params: { days },
    })
    return response.data
  }

  async getLeaderboard(limit: number = 10): Promise<any[]> {
    const response = await this.client.get('/analytics/leaderboard', {
      params: { limit },
    })
    return response.data
  }

  // ============ Adapter Endpoints ============
  async getAdapterConfig(): Promise<Record<string, unknown>> {
    const response = await this.client.get('/adapter/config')
    return response.data
  }

  async updateAdapterConfig(config: Record<string, unknown>): Promise<Record<string, unknown>> {
    const response = await this.client.put('/adapter/config', config)
    return response.data
  }

  async getRecommendation(sessionId: number): Promise<AdapterRecommendation> {
    const response = await this.client.post<AdapterRecommendation>('/adapter/recommend', {
      session_id: sessionId,
    })
    return response.data
  }
}

export const apiClient = new ApiClient()
