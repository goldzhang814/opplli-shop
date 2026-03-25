import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Admin {
  id:          number
  email:       string
  full_name:   string | null
  role:        'admin' | 'super_admin'
  is_active:   boolean
  permissions: Record<string, boolean>
}

export const useAuthStore = defineStore('auth', () => {
  const admin = ref<Admin | null>(null)
  const token = ref<string | null>(localStorage.getItem('admin_token'))

  const isLoggedIn    = computed(() => !!token.value)
  const isSuperAdmin  = computed(() => admin.value?.role === 'super_admin')
  const can           = (module: string) => {
    if (!admin.value) return false
    if (admin.value.role === 'super_admin') return true
    return !!admin.value.permissions?.[module]
  }

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('admin_token', t)
  }

  function setAdmin(a: Admin) {
    admin.value = a
  }

  function logout() {
    token.value = null
    admin.value = null
    localStorage.removeItem('admin_token')
  }

  return { admin, token, isLoggedIn, isSuperAdmin, can, setToken, setAdmin, logout }
})
