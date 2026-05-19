/**
 * useTyping Hook - Advanced typing test state management
 * 
 * Tracks:
 * - Character-by-character typing
 * - Keystroke events with precise timing
 * - Real-time WPM and accuracy
 * - Error classification
 */

import { create } from 'zustand'
import { TypingMetrics, TypingSession } from '@types/index'

interface KeystrokeEvent {
  character: string
  position: number
  timestamp_ms: number
  expected_char: string
}

interface TypingState {
  // Session data
  currentSession: TypingSession | null
  testText: string
  typedText: string
  isRunning: boolean
  startTime: number | null
  keystrokeEvents: KeystrokeEvent[]

  // Metrics (real-time)
  metrics: TypingMetrics | null
  realTimeWpm: number
  realTimeAccuracy: number
  realTimeErrors: number

  // UI state
  focusedCharIndex: number
  showStats: boolean

  // Actions
  initializeSession: (session: TypingSession, text: string) => void
  startTest: () => void
  stopTest: () => void
  addCharacter: (char: string) => void
  removeCharacter: () => void
  calculateMetrics: () => void
  resetTest: () => void
  recordKeystroke: (event: KeystrokeEvent) => void
}

export const useTyping = create<TypingState>((set, get) => ({
  currentSession: null,
  testText: '',
  typedText: '',
  isRunning: false,
  startTime: null,
  keystrokeEvents: [],
  metrics: null,
  realTimeWpm: 0,
  realTimeAccuracy: 0,
  realTimeErrors: 0,
  focusedCharIndex: 0,
  showStats: false,

  initializeSession: (session, text) => {
    set({
      currentSession: session,
      testText: text,
      typedText: '',
      keystrokeEvents: [],
      metrics: null,
      focusedCharIndex: 0,
      realTimeWpm: 0,
      realTimeAccuracy: 0,
      realTimeErrors: 0,
    })
  },

  startTest: () => {
    set({
      isRunning: true,
      startTime: Date.now(),
      keystrokeEvents: [],
    })
  },

  stopTest: () => {
    set({ isRunning: false })
    get().calculateMetrics()
  },

  recordKeystroke: (event: KeystrokeEvent) => {
    set((state) => ({
      keystrokeEvents: [...state.keystrokeEvents, event],
    }))
  },

  addCharacter: (char) => {
    const state = get()
    const newTypedText = state.typedText + char
    set({
      typedText: newTypedText,
      focusedCharIndex: newTypedText.length,
    })
    get().calculateMetrics()
  },

  removeCharacter: () => {
    const state = get()
    const newTypedText = state.typedText.slice(0, -1)
    set({
      typedText: newTypedText,
      focusedCharIndex: Math.max(0, state.focusedCharIndex - 1),
      keystrokeEvents: state.keystrokeEvents.slice(0, -1),
    })
    get().calculateMetrics()
  },

  calculateMetrics: () => {
    const state = get()
    if (!state.startTime) return

    const typedText = state.typedText
    const testText = state.testText
    const durationMs = Date.now() - state.startTime
    const durationMinutes = durationMs / 60000

    // Calculate WPM (standard: 5 characters = 1 word)
    const wpm = durationMinutes > 0 ? (typedText.length / 5) / durationMinutes : 0

    // Calculate accuracy (correct characters / total expected)
    let correctChars = 0
    for (let i = 0; i < Math.min(typedText.length, testText.length); i++) {
      if (typedText[i] === testText[i]) {
        correctChars++
      }
    }
    const accuracy = testText.length > 0 ? (correctChars / testText.length) * 100 : 0

    // Calculate errors (character-level)
    let errorCount = 0
    for (let i = 0; i < Math.max(typedText.length, testText.length); i++) {
      const typedChar = typedText[i] || ''
      const expectedChar = testText[i] || ''
      if (typedChar !== expectedChar) {
        errorCount++
      }
    }

    set({
      realTimeWpm: Math.round(wpm * 100) / 100,
      realTimeAccuracy: Math.round(accuracy * 100) / 100,
      realTimeErrors: errorCount,
      metrics: {
        wpm: Math.round(wpm * 100) / 100,
        accuracy: Math.round(accuracy * 100) / 100,
        errors: errorCount,
        key_presses: typedText.length,
      },
    })
  },

  resetTest: () => {
    set({
      testText: '',
      typedText: '',
      isRunning: false,
      startTime: null,
      keystrokeEvents: [],
      metrics: null,
      realTimeWpm: 0,
      realTimeAccuracy: 0,
      realTimeErrors: 0,
      focusedCharIndex: 0,
    })
  },
}))
