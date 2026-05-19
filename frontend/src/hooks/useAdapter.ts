/**
 * useAdapter hook - Adapter and difficulty management
 */

import { create } from 'zustand'
import { AdapterRecommendation } from '@types/index'
import { adapterService } from '@services/adapter'

interface AdapterState {
  currentDifficulty: number
  adapterType: string
  recommendation: AdapterRecommendation | null
  isLoading: boolean
  error: string | null

  // Actions
  getRecommendation: (sessionId: number) => Promise<void>
  updateDifficulty: (difficulty: number) => void
  setAdapterType: (type: string) => Promise<void>
}

export const useAdapter = create<AdapterState>((set) => ({
  currentDifficulty: 1,
  adapterType: 'rule_based',
  recommendation: null,
  isLoading: false,
  error: null,

  getRecommendation: async (sessionId) => {
    set({ isLoading: true })
    try {
      const recommendation = await adapterService.getRecommendation(sessionId)
      set({
        recommendation,
        currentDifficulty: recommendation.next_difficulty,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.message,
        isLoading: false,
      })
    }
  },

  updateDifficulty: (difficulty) => {
    set({ currentDifficulty: Math.max(1, Math.min(10, difficulty)) })
  },

  setAdapterType: async (type) => {
    try {
      await adapterService.updateConfig({ adapter_type: type })
      set({ adapterType: type })
    } catch (error: any) {
      set({ error: error.message })
    }
  },
}))
