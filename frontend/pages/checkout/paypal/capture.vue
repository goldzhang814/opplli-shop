<template>
  <div class="container-store py-20 text-center max-w-md mx-auto">
    <div v-if="processing" class="space-y-4">
      <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-emerald-500 animate-spin" />
      </div>
      <h2 class="font-head text-xl font-bold text-zinc-900">Processing your payment…</h2>
      <p class="text-zinc-500 text-sm">Please wait, do not close this tab.</p>
    </div>
    <div v-else-if="error" class="space-y-4">
      <div class="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
        <UIcon name="i-heroicons-x-circle" class="w-8 h-8 text-red-500" />
      </div>
      <h2 class="font-head text-xl font-bold text-zinc-900">Payment failed</h2>
      <p class="text-zinc-500 text-sm">{{ error }}</p>
      <UButton to="/checkout">Try Again</UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const route      = useRoute()
const api        = useApi()
const processing = ref(true)
const error      = ref('')

onMounted(async () => {
  try {
    const orderId = route.query.order_id as string
    const token   = route.query.token   as string
    await $fetch(`${useRuntimeConfig().public.apiBase}/api/v1/payments/paypal/capture`, {
      query: { order_id: orderId, token },
    })
    await navigateTo(`/orders/${orderId}?success=1`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Payment could not be completed'
    processing.value = false
  }
})
</script>
