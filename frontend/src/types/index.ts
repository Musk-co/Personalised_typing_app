/**
 * Type definitions for the frontend application
 */

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  created_at: string
}

export interface TypingMetrics {
  wpm: number
  accuracy: number
  errors: number
  key_presses: number
}

export interface TypingSession {
  id: number
  user_id: number
  test_type: string
  difficulty_level: number
  metrics: TypingMetrics
  status: 'in_progress' | 'completed' | 'paused'
  started_at: string
  ended_at?: string
}

export interface AdapterRecommendation {
  next_difficulty: number
  focus_areas: string[]
  reason: string
  confidence: number
}

export interface UserStats {
  total_sessions: number
  avg_wpm: number
  avg_accuracy: number
  best_wpm: number
  total_errors: number
  improvement_trend?: number
}

export interface ProgressPoint {
  date: string
  wpm: number
  accuracy: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiError {
  detail: string
  status_code: number
}
