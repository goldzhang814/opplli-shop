export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (!auth.token) {
    return navigateTo(`/auth/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }
})
