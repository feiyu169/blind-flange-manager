import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const response = await api.post('/api/v1/users/login', {
      username,
      password,
    })
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', token.value)
    return response.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/api/v1/users/me')
      user.value = response.data
    } catch (error) {
      logout()
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    fetchUser,
  }
})
