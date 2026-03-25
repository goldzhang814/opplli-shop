<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="logo-icon">A</div>
        <h1>Admin Panel</h1>
        <p>Sign in to your account</p>
      </div>

      <n-form ref="formRef" :model="form" :rules="rules" size="large">
        <n-form-item path="email" label="Email">
          <n-input v-model:value="form.email" type="text" placeholder="admin@example.com"
            @keydown.enter="submit" />
        </n-form-item>
        <n-form-item path="password" label="Password">
          <n-input v-model:value="form.password" type="password" show-password-on="mousedown"
            placeholder="Password" @keydown.enter="submit" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" size="large" style="margin-top:8px" @click="submit">
          Sign In
        </n-button>
      </n-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { api, errMsg } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'

const router  = useRouter()
const auth    = useAuthStore()
const message = useMessage()
const formRef = ref()
const loading = ref(false)

const form = reactive({ email: '', password: '' })
const rules = {
  email:    [{ required: true, message: 'Email required' }],
  password: [{ required: true, message: 'Password required' }],
}

async function submit() {
  try { await formRef.value?.validate() } catch { return }
  loading.value = true
  try {
    const res  = await api.login(form)
    auth.setToken(res.data.access_token)
    const me   = await api.me()
    auth.setAdmin(me.data)
    await router.push('/')
  } catch (e) {
    message.error(errMsg(e))
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; background: #18181b;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.login-card {
  width: 100%; max-width: 400px;
  background: #27272a; border-radius: 16px; padding: 36px;
  border: 1px solid #3f3f46;
}
.login-logo { text-align: center; margin-bottom: 28px; }
.logo-icon {
  width: 48px; height: 48px; background: #10b981; border-radius: 12px;
  color: #fff; font-size: 20px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; margin: 0 auto 12px;
}
.login-logo h1 { color: #f4f4f5; font-size: 22px; font-weight: 600; margin-bottom: 4px; }
.login-logo p  { color: #71717a; font-size: 14px; }

:deep(.n-form-item-label) { color: #a1a1aa !important; }
:deep(.n-input) { background: #18181b !important; }
:deep(.n-input .n-input__input-el) { color: #f4f4f5 !important; }
</style>
