/**
 * Adapter communication service
 * Handles interaction with the typing adaptation engine
 */

import { apiClient } from './api'
import { AdapterRecommendation } from '@types/index'

export const adapterService = {
  /**
   * Get current adapter configuration
   */
  async getConfig() {
    return apiClient.getAdapterConfig()
  },

  /**
   * Update adapter configuration
   */
  async updateConfig(config: Record<string, unknown>) {
    return apiClient.updateAdapterConfig(config)
  },

  /**
   * Get difficulty recommendation for next session
   */
  async getRecommendation(sessionId: number): Promise<AdapterRecommendation> {
    return apiClient.getRecommendation(sessionId)
  },

  /**
   * Calculate difficulty based on performance
   */
  calculateDifficulty(wpm: number, accuracy: number): number {
    if (accuracy < 70) return 1
    if (wpm < 30) return 1
    if (wpm < 40) return 2
    if (wpm < 50) return 3
    if (wpm < 60) return 4
    if (wpm < 70) return 5
    if (wpm < 80) return 6
    if (wpm < 90) return 7
    return 8
  },

  /**
   * Get focus areas based on performance
   */
  getFocusAreas(accuracy: number, wpm: number): string[] {
    const areas = []
    if (accuracy < 85) areas.push('Accuracy')
    if (wpm < 50) areas.push('Speed')
    if (areas.length === 0) areas.push('Push for higher difficulty')
    return areas
  },
}
