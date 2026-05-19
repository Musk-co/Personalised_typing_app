/**
 * Local storage utilities
 */

export const storageService = {
  // Token management
  getToken: () => localStorage.getItem('access_token'),
  setToken: (token: string) => localStorage.setItem('access_token', token),
  clearToken: () => localStorage.removeItem('access_token'),

  // User data
  getUser: () => {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },
  setUser: (user: any) => localStorage.setItem('user', JSON.stringify(user)),
  clearUser: () => localStorage.removeItem('user'),

  // Session data
  getSessionDraft: (sessionId: string) => {
    const draft = localStorage.getItem(`session_draft_${sessionId}`)
    return draft ? JSON.parse(draft) : null
  },
  setSessionDraft: (sessionId: string, data: any) =>
    localStorage.setItem(`session_draft_${sessionId}`, JSON.stringify(data)),
  clearSessionDraft: (sessionId: string) => localStorage.removeItem(`session_draft_${sessionId}`),

  // Settings
  getPreferences: () => {
    const prefs = localStorage.getItem('preferences')
    return prefs ? JSON.parse(prefs) : {}
  },
  setPreferences: (preferences: any) =>
    localStorage.setItem('preferences', JSON.stringify(preferences)),

  // Clear all
  clear: () => localStorage.clear(),
}
