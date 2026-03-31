<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">{{ $t('auth.signUp') }}</h1>
      </template>

      <form class="space-y-4" @submit.prevent="submit">
        <UFormGroup :label="$t('auth.email')" :error="errors.email">
          <UInput v-model="form.email" type="email" autocomplete="email" placeholder="you@example.com" />
        </UFormGroup>

        <UFormGroup :label="$t('auth.password')" :error="errors.password">
          <UInput
            v-model="form.password"
            :type="showPw ? 'text' : 'password'"
            autocomplete="new-password"
            placeholder="Min. 8 characters"
          >
            <template #trailing>
              <UButton :icon="showPw ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                type="button" variant="link" color="gray" @click="showPw = !showPw" />
            </template>
          </UInput>
        </UFormGroup>

        <UFormGroup :label="$t('auth.confirmPassword')" :error="errors.confirm">
          <UInput v-model="form.confirm" :type="showPw ? 'text' : 'password'"
            autocomplete="new-password" placeholder="Repeat password" />
        </UFormGroup>

        <UFormGroup :label="$t('auth.languageLabel')">
          <USelect v-model="form.language_code" :options="langOptions" />
        </UFormGroup>

        <UFormGroup :error="errors.agree">
          <UCheckbox v-model="form.agree_terms" :label="$t('auth.agreeTerms')" />
        </UFormGroup>

        <UButton type="submit" size="lg" block :loading="loading">
          {{ $t('auth.signUp') }}
        </UButton>
      </form>

      <template #footer>
        <p class="text-center text-sm text-zinc-500">
          {{ $t('auth.hasAccount') }}
          <NuxtLink to="/auth/login" class="text-emerald-600 font-semibold hover:underline">
            {{ $t('auth.signIn') }}
          </NuxtLink>
        </p>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { t } = useI18n()
const route  = useRoute()
const auth   = useAuthStore()
const api    = useApi()
const toast  = useToast()

const form = reactive({
  email:         '',
  password:      '',
  confirm:       '',
  agree_terms:   false,
  language_code: 'en',
})
const errors  = reactive({ email: '', password: '', confirm: '', agree: '' })
const showPw  = ref(false)
const loading = ref(false)

const langOptions = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Español' },
]

onMounted(() => {
  const q = route.query.email
  if (!form.email && typeof q === 'string') {
    form.email = q
  } else if (!form.email && auth.user?.email) {
    form.email = auth.user.email
  }
})

async function submit() {
  Object.keys(errors).forEach(k => (errors as any)[k] = '')

  if (form.password !== form.confirm) {
    errors.confirm = 'Passwords do not match'
    return
  }
  if (!form.agree_terms) {
    errors.agree = 'You must agree to the terms'
    return
  }

  loading.value = true
  try {
    const res  = await api.register({
      email:         form.email,
      password:      form.password,
      agree_terms:   form.agree_terms,
      language_code: form.language_code,
    }) as any
    auth.setToken(res.access_token)
    const user = await api.me() as any
    auth.setUser(user)
    await navigateTo('/')
    toast.add({ title: 'Account created! Welcome 🎉', color: 'green' })
  } catch (e: any) {
    const msg = e?.data?.detail || t('common.error')
    errors.email = msg
  } finally {
    loading.value = false
  }
}
</script>
