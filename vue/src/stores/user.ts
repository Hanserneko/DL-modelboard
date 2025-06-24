import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const username = ref('')

  const login = (name: string) => {
    isLoggedIn.value = true
    username.value = name
    localStorage.setItem('user', JSON.stringify({ name }))
  }

  const logout = () => {
    isLoggedIn.value = false
    username.value = ''
    localStorage.removeItem('user')
  }

  const init = () => {
    const data = localStorage.getItem('user')
    if (data) {
      const parsed = JSON.parse(data)
      isLoggedIn.value = true
      username.value = parsed.name
    }
  }

  return {
    isLoggedIn,
    username,
    login,
    logout,
    init,
  }
})
