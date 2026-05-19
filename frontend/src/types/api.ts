/**
 * API response types
 */

import { User, TypingSession, TypingMetrics } from './index'

export interface SessionCreateRequest {
  test_type: string
  difficulty_level: number
  custom_text?: string
  adapter_config?: Record<string, unknown>
}

export interface SessionUpdateRequest {
  metrics: TypingMetrics
  status: string
  end_time?: string
}
