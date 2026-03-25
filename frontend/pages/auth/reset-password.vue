<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">New Password</h1>
      </template>

      <form class="space-y-4" @submit.prevent="submit">
        <UFormGroup label="New Password" :error="error">
          <UInput v-model="password" type="password" placeholder="Min. 8 characters" required />
        </UFormGroup>
        <UFormGroup label="Confirm Password">
          <UInput v-model="confirm" type="password" required />
        </UFormGroup>
        <UButton type="submit" size="lg" block :loading="loading">Set New Password</UButton>
      </form>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })
const route   = useRoute()
const api     = useApi()
const toast   = useToast()
const password= ref('')
const confirm = ref('')
const loading = ref(false)
const error   = ref('')

async function submit() {
  if (password.value !== confirm.value) { error.value = 'Passwords do not match'; return }
  loading.value = true
  try {
    await api.resetPassword({ token: route.query.token as string, new_password: password.value })
    toast.add({ title: 'Password updated! Please sign in.', color: 'green' })
    await navigateTo('/auth/login')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Invalid or expired token'
  } finally { loading.value = false }
}
</script>
