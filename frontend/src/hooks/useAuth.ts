/**
 * useAuth hook - Authentication state management
 */

import { create } from 'zustand'
import { User, AuthResponse } from '@types/index'
import { apiClient } from '@services/api'
import { storageService } from '@services/storage'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

export const useAuth = create<AuthState>((set) => ({
  user: storageService.getUser(),
  isAuthenticated: !!storageService.getToken(),
  isLoading: false,
  error: null,

  register: async (email, username, password, fullName) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.register(email, username, password, fullName)
      storageService.setToken(response.access_token)
      storageService.setUser(response.user)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      })
      throw error
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.login(email, password)
      storageService.setToken(response.access_token)
      storageService.setUser(response.user)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: async () => {
    set({ isLoading: true })
    try {
      await apiClient.logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
    storageService.clearToken()
    storageService.clearUser()
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
  },

  checkAuth: async () => {
    const token = storageService.getToken()
    if (!token) {
      set({ isAuthenticated: false })
      return
    }

    try {
      const user = await apiClient.getCurrentUser()
      storageService.setUser(user)
      set({
        user,
        isAuthenticated: true,
      })
    } catch (error) {
      storageService.clearToken()
      storageService.clearUser()
      set({
        isAuthenticated: false,
        user: null,
      })
    }
  },
}))
