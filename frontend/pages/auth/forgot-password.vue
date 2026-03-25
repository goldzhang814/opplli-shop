<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">{{ $t('auth.resetPassword') }}</h1>
        <p class="text-sm text-zinc-400 text-center mt-1">Enter your email and we'll send you a reset link.</p>
      </template>

      <div v-if="sent" class="text-center py-4">
        <div class="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-envelope" class="w-6 h-6 text-emerald-600" />
        </div>
        <p class="text-zinc-600 text-sm">{{ $t('auth.resetSent') }}</p>
      </div>

      <form v-else class="space-y-4" @submit.prevent="submit">
        <UFormGroup :label="$t('auth.email')">
          <UInput v-model="email" type="email" placeholder="you@example.com" required />
        </UFormGroup>
        <UButton type="submit" size="lg" block :loading="loading">Send Reset Link</UButton>
      </form>

      <template #footer>
        <p class="text-center text-sm text-zinc-500">
          <NuxtLink to="/auth/login" class="text-emerald-600 hover:underline">← Back to Sign In</NuxtLink>
        </p>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })
const api     = useApi()
const email   = ref('')
const loading = ref(false)
const sent    = ref(false)

async function submit() {
  loading.value = true
  try {
    await api.forgotPassword({ email: email.value })
    sent.value = true
  } finally { loading.value = false }
}
</script>
