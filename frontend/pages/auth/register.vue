<template>
  <div>
    <UCard class="shadow-xl rounded-3xl border-zinc-100">
      <template #header>
        <h1 class="font-head text-2xl font-bold text-zinc-900 text-center">
          {{ step === 1 ? 'Create Account' : step === 2 ? 'Enter Verification Code' : 'Complete Registration' }}
        </h1>
        <p class="text-sm text-zinc-400 text-center mt-1">
          {{ step === 1 ? 'Enter your email to get started' : step === 2 ? `Code sent to ${form.email}` : 'Almost done!' }}
        </p>
      </template>

      <!-- Step 1: Email input -->
      <div v-if="step === 1" class="space-y-4">
        <UFormGroup label="Email Address" :error="errors.email">
          <UInput v-model="form.email" type="email" placeholder="you@example.com"
            autocomplete="email" @keydown.enter="sendCode" />
        </UFormGroup>
        <UButton block size="lg" :loading="loading" @click="sendCode">
          Send Verification Code
        </UButton>
      </div>

      <!-- Step 2: OTP input -->
      <div v-else-if="step === 2" class="space-y-4">
        <p class="text-sm text-zinc-500 text-center">
          We sent a 6-digit code to <strong>{{ form.email }}</strong>
        </p>

        <!-- OTP input boxes -->
        <div class="flex justify-center gap-3 my-6">
          <input
            v-for="(_, i) in otp"
            :key="i"
            :ref="el => otpRefs[i] = el as HTMLInputElement"
            v-model="otp[i]"
            type="text"
            inputmode="numeric"
            maxlength="1"
            class="otp-box"
            @input="onOtpInput(i)"
            @keydown.backspace="onOtpBackspace(i)"
            @paste.prevent="onOtpPaste($event)"
          />
        </div>

        <UButton block size="lg" :loading="loading" :disabled="otp.join('').length < 6" @click="verifyCode">
          Verify Code
        </UButton>

        <p class="text-center text-sm text-zinc-400">
          Didn't receive it?
          <button
            class="text-emerald-600 hover:underline disabled:opacity-40"
            :disabled="resendCooldown > 0"
            @click="sendCode(true)"
          >
            Resend {{ resendCooldown > 0 ? `(${resendCooldown}s)` : '' }}
          </button>
        </p>

        <button class="block text-center text-sm text-zinc-400 hover:text-zinc-600 w-full" @click="step = 1">
          ← Change email
        </button>
      </div>

      <!-- Step 3: Complete registration -->
      <div v-else class="space-y-4">
        <UFormGroup label="Password" :error="errors.password">
<!--          <UInput v-model="form.password" :type="showPw ? 'text' : 'password'"
            placeholder="Min. 8 characters" autocomplete="new-password">
            <template #trailing>
              <UButton :icon="showPw ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                type="button" variant="link" color="gray" @click="showPw = !showPw" />
            </template>
          </UInput>-->
          <div style="position:relative">
            <UInput
              v-model="form.password"
              :type="showPw ? 'text' : 'password'"
              placeholder="Min. 8 characters"
              autocomplete="new-password"
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

        <UFormGroup label="Confirm Password" :error="errors.confirm">
<!--          <UInput v-model="form.confirm" type="password"
            placeholder="Repeat password" autocomplete="new-password" />-->

          <div style="position:relative">
            <UInput
              v-model="form.confirm"
              :type="showPw ? 'text' : 'password'"
              placeholder="Repeat password"
              autocomplete="new-password"
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

        <UFormGroup label="Preferred Language">
          <USelect v-model="form.language_code" :options="langOptions" />
        </UFormGroup>

        <UFormGroup :error="errors.agree">
          <UCheckbox v-model="form.agree_terms" label="I agree to the Terms of Service and Privacy Policy" />
        </UFormGroup>

        <UButton type="button" block size="lg" :loading="loading" @click="submit">
          Create Account
        </UButton>
      </div>

      <template #footer>
        <p class="text-center text-sm text-zinc-500">
          Already have an account?
          <NuxtLink to="/auth/login" class="text-emerald-600 font-semibold hover:underline">
            Sign In
          </NuxtLink>
        </p>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { t }  = useI18n()
const auth   = useAuthStore()
const api    = useApi()
const toast  = useToast()

const step   = ref(1)
const loading= ref(false)
const showPw = ref(false)

const form = reactive({
  email:              '',
  password:           '',
  confirm:            '',
  agree_terms:        false,
  language_code:      'en',
  verification_token: '',
})
const errors = reactive({ email:'', password:'', confirm:'', agree:'' })

// ── OTP boxes ─────────────────────────────────────────────────────────────────
const otp     = ref(['','','','','',''])
const otpRefs = ref<HTMLInputElement[]>([])

function onOtpInput(i: number) {
  const val = otp.value[i]
  if (val && i < 5) {
    nextTick(() => otpRefs.value[i + 1]?.focus())
  }
}

function onOtpBackspace(i: number) {
  if (!otp.value[i] && i > 0) {
    otp.value[i - 1] = ''
    nextTick(() => otpRefs.value[i - 1]?.focus())
  }
}

function onOtpPaste(e: ClipboardEvent) {
  const text = e.clipboardData?.getData('text') || ''
  const digits = text.replace(/\D/g, '').slice(0, 6)
  digits.split('').forEach((d, i) => { otp.value[i] = d })
  nextTick(() => otpRefs.value[Math.min(digits.length, 5)]?.focus())
}

// ── Resend cooldown ───────────────────────────────────────────────────────────
const resendCooldown = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

function startCooldown() {
  resendCooldown.value = 60
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

// ── Step 1: Send code ─────────────────────────────────────────────────────────
async function sendCode(isResend = false) {
  errors.email = ''
  if (!form.email || !form.email.includes('@')) {
    errors.email = 'Please enter a valid email'
    return
  }
  loading.value = true
  try {
    await api.sendVerification(form.email)
    otp.value = ['','','','','','']
    step.value = 2
    startCooldown()
    if (isResend) toast.add({ title: 'New code sent!', color: 'green' })
    nextTick(() => otpRefs.value[0]?.focus())
  } catch (e: any) {
    errors.email = e?.data?.detail || t('common.error')
    if (isResend) toast.add({ title: errors.email, color: 'red' })
  } finally {
    loading.value = false
  }
}

// ── Step 2: Verify code ───────────────────────────────────────────────────────
async function verifyCode() {
  loading.value = true
  try {
    const res = await api.verifyCode(form.email, otp.value.join('')) as any
    form.verification_token = res.verification_token
    step.value = 3
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || 'Invalid code', color: 'red' })
    otp.value = ['','','','','','']
    nextTick(() => otpRefs.value[0]?.focus())
  } finally {
    loading.value = false
  }
}

// ── Step 3: Register ──────────────────────────────────────────────────────────
async function submit() {
  Object.keys(errors).forEach(k => (errors as any)[k] = '')
  if (form.password.length < 8)          { errors.password = 'Min. 8 characters'; return }
  if (form.password !== form.confirm)    { errors.confirm  = 'Passwords do not match'; return }
  if (!form.agree_terms)                 { errors.agree    = 'You must agree to the terms'; return }

  loading.value = true
  try {
    const res  = await api.register({
      email:              form.email,
      password:           form.password,
      agree_terms:        form.agree_terms,
      language_code:      form.language_code,
      verification_token: form.verification_token,
    }) as any
    auth.setToken(res.access_token)
    const user = await api.me() as any
    auth.setUser(user)
    await navigateTo('/')
    toast.add({ title: 'Account created! Welcome 🎉', color: 'green' })
  } catch (e: any) {
    const msg = e?.data?.detail || t('common.error')
    // Token expired → send back to step 1
    if (msg.includes('verification')) {
      toast.add({ title: 'Verification expired. Please start again.', color: 'red' })
      step.value = 1
    } else {
      errors.email = msg
    }
  } finally {
    loading.value = false
  }
}

const langOptions = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Español' },
]
</script>

<style scoped>
.otp-box {
  width: 48px;
  height: 56px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.15s;
  color: #18181b;
  caret-color: transparent;
}
.otp-box:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16,185,129,0.15);
}
</style>