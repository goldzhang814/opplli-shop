import { defineStore } from 'pinia'

interface User {
  id:            number
  email:         string
  full_name:     string | null
  avatar_url:    string | null
  language_code: string
  is_guest:      boolean
  is_active:     boolean
}

const TOKEN_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user:  null as User | null,
    // Read token from localStorage immediately on store creation (client only)
    token: (import.meta.client ? localStorage.getItem(TOKEN_KEY) : null) as string | null,
  }),

  getters: {
    isLoggedIn:  (s) => !!s.token && !s.user?.is_guest,
    isGuest:     (s) => !!s.token && !!s.user?.is_guest,
    displayName: (s) => s.user?.full_name || s.user?.email || '',
  },

  actions: {
    setToken(token: string) {
      this.token = token
      if (import.meta.client) {
        localStorage.setItem(TOKEN_KEY, token)
      }
    },

    setUser(user: User) {
      this.user = user
    },

    logout() {
      this.token = null
      this.user  = null
      if (import.meta.client) {
        localStorage.removeItem(TOKEN_KEY)
      }
    },
  },
})
