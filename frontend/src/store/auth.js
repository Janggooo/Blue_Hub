import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('bluehub_token') || null,
    user: JSON.parse(localStorage.getItem('bluehub_user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    role: (state) => state.user?.role || null,
  },

  actions: {
    async login(email, password) {
      const { data } = await axios.post('/api/login', { email, password })
      this.setSession(data.user, data.access_token)
    },

    async register(payload) {
      const { data } = await axios.post('/api/register', payload)
      this.setSession(data.user, data.access_token)
    },

    setSession(user, token) {
      this.user = user
      this.token = token
      localStorage.setItem('bluehub_token', token)
      localStorage.setItem('bluehub_user', JSON.stringify(user))
    },

    clearSession() {
      this.user = null
      this.token = null
      localStorage.removeItem('bluehub_token')
      localStorage.removeItem('bluehub_user')
    },

    async logout() {
      try {
        await axios.post('/api/logout', {}, { headers: { Authorization: `Bearer ${this.token}` } })
      } catch (e) {
        // ignore network errors on logout
      }
      this.clearSession()
    }
  }
})
