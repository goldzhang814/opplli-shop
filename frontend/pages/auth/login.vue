<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">{{ $t('auth.signIn') }}</h1>
        <p class="text-sm text-zinc-400 text-center mt-1">Welcome back!</p>
      </template>

      <!-- OAuth buttons -->
      <div class="space-y-2 mb-5">
        <a
          :href="googleHref"
          class="flex items-center justify-center gap-3 w-full border border-zinc-200 rounded-xl py-2.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors"
        >
          <img src="/icons/google.svg" alt="Google" class="w-5 h-5" />
          Continue with {{ $t('auth.google') }}
        </a>
<!--        <a
          :href="facebookHref"
          class="flex items-center justify-center gap-3 w-full bg-[#1877F2] text-white rounded-xl py-2.5 text-sm font-medium hover:bg-[#166FE5] transition-colors"
        >
          <UIcon name="i-lucide-facebook" class="w-5 h-5" />
          Continue with {{ $t('auth.facebook') }}
        </a>-->
      </div>

      <UDivider :label="$t('auth.orContinueWith')" class="mb-5" />

      <!-- Email form -->
      <form class="space-y-4" @submit.prevent="submit">
        <UFormGroup :label="$t('auth.email')" :error="errors.email">
          <UInput v-model="form.email" type="email" autocomplete="email" placeholder="you@example.com" />
        </UFormGroup>

        <UFormGroup :label="$t('auth.password')" :error="errors.password">
<!--          <UInput
            v-model="form.password"
            :type="showPw ? 'text' : 'password'"
            autocomplete="current-password"
            placeholder="••••••••"
          >
            <template #trailing>
              <UButton
                :icon="showPw ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                type="button"
                variant="link"
                color="gray"
                @click="showPw = !showPw"
              />
            </template>
          </UInput>-->

          <div style="position:relative">
  <UInput
    v-model="form.password"
    :type="showPw ? 'text' : 'password'"
    autocomplete="current-password"
    placeholder="••••••••"
  />
  <button
    type="button"
    style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:#9ca3af;padding:0;line-height:1"
    @click.prevent.stop="showPw = !showPw"
  >
    <UIcon :name="showPw ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" style="width:18px;height:18px"/>
  </button>
</div>
        </UFormGroup>

        <div class="flex justify-end">
          <NuxtLink to="/auth/forgot-password" class="text-xs text-emerald-600 hover:underline">
            {{ $t('auth.forgotPassword') }}
          </NuxtLink>
        </div>

        <UButton type="submit" size="lg" block :loading="loading">
          {{ $t('auth.signIn') }}
        </UButton>
      </form>

      <template #footer>
        <p class="text-center text-sm text-zinc-500">
          {{ $t('auth.noAccount') }}
          <NuxtLink to="/auth/register" class="text-emerald-600 font-semibold hover:underline">
            {{ $t('auth.signUp') }}
          </NuxtLink>
        </p>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { t }   = useI18n()
const config  = useRuntimeConfig()
const auth    = useAuthStore()
const cart    = useCartStore()
const api     = useApi()
const toast   = useToast()
const route   = useRoute()
const redirect = computed(() => route.query.redirect as string | undefined)

const googleHref = computed(() => {
  const base = `${config.public.apiBase}/api/v1/auth/google`
  return redirect.value ? `${base}?redirect=${encodeURIComponent(redirect.value)}` : base
})

const facebookHref = computed(() => {
  const base = `${config.public.apiBase}/api/v1/auth/facebook`
  return redirect.value ? `${base}?redirect=${encodeURIComponent(redirect.value)}` : base
})

const form   = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const showPw = ref(false)
const loading= ref(false)

async function submit() {
  errors.email    = ''
  errors.password = ''
  loading.value   = true
  try {
    const res  = await api.login(form) as any
    auth.setToken(res.access_token)
    const user = await api.me() as any
    auth.setUser(user)

    // Merge guest cart if any
    if (cart.guestToken) {
      await api.mergeCart(cart.guestToken).catch(() => {})
    }

    const redirect = route.query.redirect as string || '/'
    await navigateTo(redirect)
    toast.add({ title: 'Welcome back!', color: 'green' })
  } catch (e: any) {
    const msg = e?.data?.detail || t('common.error')
    if (msg.toLowerCase().includes('password')) errors.password = msg
    else errors.email = msg
  } finally {
    loading.value = false
  }
}
</script>
