/**
 * useSession hook - Session management
 */

import { create } from 'zustand'
import { TypingSession } from '@types/index'
import { apiClient } from '@services/api'

interface SessionState {
  sessions: TypingSession[]
  currentSession: TypingSession | null
  isLoading: boolean
  error: string | null

  // Actions
  fetchSessions: () => Promise<void>
  createSession: (data: any) => Promise<TypingSession>
  updateSession: (sessionId: number, data: any) => Promise<TypingSession>
  getSession: (sessionId: number) => Promise<TypingSession>
  setCurrentSession: (session: TypingSession | null) => void
}

export const useSession = create<SessionState>((set) => ({
  sessions: [],
  currentSession: null,
  isLoading: false,
  error: null,

  fetchSessions: async () => {
    set({ isLoading: true })
    try {
      const sessions = await apiClient.listSessions()
      set({ sessions, isLoading: false })
    } catch (error: any) {
      set({
        error: error.message,
        isLoading: false,
      })
    }
  },

  createSession: async (data) => {
    set({ isLoading: true })
    try {
      const session = await apiClient.createSession(data)
      set({
        currentSession: session,
        sessions: [session, ...get().sessions],
        isLoading: false,
      })
      return session
    } catch (error: any) {
      set({
        error: error.message,
        isLoading: false,
      })
      throw error
    }
  },

  updateSession: async (sessionId, data) => {
    try {
      const session = await apiClient.updateSession(sessionId, data)
      set((state) => ({
        sessions: state.sessions.map((s) => (s.id === sessionId ? session : s)),
        currentSession: state.currentSession?.id === sessionId ? session : state.currentSession,
      }))
      return session
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  getSession: async (sessionId) => {
    try {
      return await apiClient.getSession(sessionId)
    } catch (error: any) {
      set({ error: error.message })
      throw error
    }
  },

  setCurrentSession: (session) => {
    set({ currentSession: session })
  },
}))

function get() {
  // This will be provided by zustand
  throw new Error('Not in store context')
}
