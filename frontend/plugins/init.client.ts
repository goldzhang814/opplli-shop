/**
 * Client-side init plugin
 * Runs once on mount: if token exists but user profile is missing, fetch it.
 */
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  const cart = useCartStore()
  const api  = useApi()

  // Init guest token
  cart.initGuestToken()

  // Token exists (restored from localStorage) but user object lost after refresh
  if (auth.token && !auth.user) {
    try {
      const user = await api.me() as any
      auth.setUser(user)
    } catch {
      // Token expired or invalid — clear it
      auth.logout()
    }
  }

  // Load cart
  if (auth.token || cart.guestToken) {
    try {
      const cartData = await api.getCart() as any
      cart.setCart(cartData)
    } catch { /* silent */ }
  }
})
