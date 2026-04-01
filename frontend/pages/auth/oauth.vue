<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">Signing you in</h1>
        <p class="text-sm text-zinc-400 text-center mt-1">Please wait while we complete your login.</p>
      </template>

      <div class="text-center text-sm text-zinc-600">
        <p v-if="status === 'loading'">Completing authentication¡­</p>
        <p v-else-if="status === 'success'">Login successful. Redirecting¡­</p>
        <p v-else>Login failed. Please try again.</p>
      </div>

      <template #footer>
        <div class="text-center">
          <NuxtLink v-if="status === 'error'" to="/auth/login" class="text-emerald-600 font-semibold hover:underline">
            Back to Sign In
          </NuxtLink>
        </div>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const auth  = useAuthStore()
const cart  = useCartStore()
const api   = useApi()
const toast = useToast()

const status = ref<'loading' | 'success' | 'error'>('loading')

function safeRedirectPath(raw: string | null): string {
  if (!raw) return '/'
  if (raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('//')) return '/'
  if (!raw.startsWith('/')) return '/'
  return raw
}

onMounted(async () => {
  const hash = window.location.hash.startsWith('#') ? window.location.hash.slice(1) : ''
  const params = new URLSearchParams(hash)
  const token = params.get('token')
  const redirect = safeRedirectPath(params.get('redirect'))

  // Clean up URL (remove token fragment)
  window.history.replaceState(null, '', '/auth/oauth')

  if (!token) {
    status.value = 'error'
    return
  }

  auth.setToken(token)
  try {
    const user = await api.me() as any
    auth.setUser(user)

    if (cart.guestToken) {
      await api.mergeCart(cart.guestToken).catch(() => {})
    }

    status.value = 'success'
    toast.add({ title: 'Login successful', color: 'green' })
    await navigateTo(redirect)
  } catch (e) {
    auth.logout()
    status.value = 'error'
  }
})
</script>
