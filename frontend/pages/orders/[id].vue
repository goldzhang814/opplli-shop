<template>
  <div class="container-store py-10 max-w-3xl">
    <div v-if="auth.isGuest" class="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6 flex items-start gap-3">
      <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-amber-800">You are viewing orders as a guest.</p>
        <p class="text-xs text-amber-700 mt-0.5">Set a password to keep access to your order history.</p>
      </div>
      <UButton size="sm" color="amber" :to="registerLink">Set Password</UButton>
    </div>
    <!-- Success banner -->
    <div v-if="route.query.success" class="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 mb-6 flex gap-3">
      <UIcon name="i-heroicons-check-circle" class="w-6 h-6 text-emerald-500 flex-shrink-0 mt-0.5" />
      <div>
        <p class="font-semibold text-emerald-800">Order confirmed!</p>
        <p class="text-sm text-emerald-600 mt-0.5">We'll send you an email confirmation shortly.</p>
      </div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-32 bg-zinc-100 rounded-2xl animate-pulse" />
    </div>

    <div v-else-if="order">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6 flex-wrap gap-4">
        <div>
          <NuxtLink to="/orders" class="text-sm text-emerald-600 hover:underline flex items-center gap-1 mb-2">
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            {{ $t('order.title') }}
          </NuxtLink>
          <h1 class="font-head text-2xl font-bold text-zinc-900">
            {{ $t('order.orderNo', { no: order.order_no }) }}
          </h1>
          <p class="text-sm text-zinc-400 mt-1">{{ $t('order.orderDate') }}: {{ formatDate(order.created_at) }}</p>
        </div>
        <OrderStatusBadge :status="order.status" />
      </div>

      <!-- Items -->
      <UCard class="rounded-2xl mb-4">
        <h2 class="font-head font-semibold text-zinc-900 mb-4">{{ $t('order.items') }}</h2>
        <div class="space-y-4">
          <div v-for="item in order.items" :key="item.id" class="flex gap-4">
            <div class="w-16 h-16 rounded-xl bg-zinc-100 overflow-hidden flex-shrink-0">
              <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-2xl">🌿</div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-zinc-900 text-sm">{{ item.product_name }}</p>
              <p v-if="item.variant_attrs" class="text-xs text-zinc-400">
                {{ Object.values(item.variant_attrs).join(' / ') }}
              </p>
              <p class="text-xs text-zinc-500 mt-0.5">Qty: {{ item.quantity }} × ${{ item.unit_price.toFixed(2) }}</p>
            </div>
            <p class="font-semibold text-zinc-900 flex-shrink-0">${{ item.subtotal.toFixed(2) }}</p>
          </div>
        </div>

        <!-- Totals -->
        <div class="border-t border-zinc-100 mt-4 pt-4 space-y-2 text-sm">
          <div class="flex justify-between text-zinc-600">
            <span>{{ $t('cart.subtotal') }}</span>
            <span>${{ order.subtotal.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between text-zinc-600">
            <span>{{ $t('checkout.shippingFee') }}</span>
            <span>{{ order.shipping_fee === 0 ? $t('common.free') : `$${order.shipping_fee.toFixed(2)}` }}</span>
          </div>
          <div v-if="order.tax_amount > 0" class="flex justify-between text-zinc-600">
            <span>{{ $t('checkout.tax') }}</span>
            <span>${{ order.tax_amount.toFixed(2) }}</span>
          </div>
          <div v-if="order.discount_amount > 0" class="flex justify-between text-emerald-600">
            <span>{{ $t('checkout.discount') }}</span>
            <span>-${{ order.discount_amount.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between font-bold text-zinc-900 border-t border-zinc-100 pt-2">
            <span class="font-head">{{ $t('checkout.total') }}</span>
            <span class="font-head text-lg">${{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>
      </UCard>

      <!-- Shipping + tracking -->
      <div class="grid sm:grid-cols-2 gap-4 mb-4">
        <UCard class="rounded-2xl">
          <h2 class="font-head font-semibold text-zinc-900 mb-3">{{ $t('order.shippingTo') }}</h2>
          <div v-if="order.shipping_address" class="text-sm text-zinc-600 space-y-1">
            <p class="font-medium text-zinc-900">{{ order.shipping_address.full_name }}</p>
            <p>{{ order.shipping_address.address_line1 }}</p>
            <p v-if="order.shipping_address.address_line2">{{ order.shipping_address.address_line2 }}</p>
            <p>{{ order.shipping_address.city }}, {{ order.shipping_address.state_code || order.shipping_address.state_name }} {{ order.shipping_address.postal_code }}</p>
            <p>{{ order.shipping_address.country_code }}</p>
          </div>
        </UCard>

        <UCard class="rounded-2xl">
          <h2 class="font-head font-semibold text-zinc-900 mb-3">{{ $t('order.paymentMethod') }}</h2>
          <p class="text-sm text-zinc-600 capitalize">{{ order.payment_method || '—' }}</p>
          <p class="text-xs text-zinc-400 mt-1">Status: {{ order.payment_status }}</p>
          <div v-if="order.shipment" class="mt-3 pt-3 border-t border-zinc-100">
            <p class="text-xs font-semibold text-zinc-500 uppercase tracking-wide mb-1">Tracking</p>
            <p class="text-sm font-medium text-zinc-900">{{ order.shipment.carrier_name }}</p>
            <a
              v-if="order.shipment.tracking_url"
              :href="order.shipment.tracking_url"
              target="_blank"
              class="text-sm text-emerald-600 hover:underline font-mono"
            >
              {{ order.shipment.tracking_no }} →
            </a>
            <p v-else class="text-sm font-mono text-zinc-600">{{ order.shipment.tracking_no }}</p>
          </div>
        </UCard>
      </div>

      <!-- Actions -->
      <div class="flex flex-wrap gap-3">
        <UButton
          v-if="order.status === 'pending_payment'"
          variant="outline"
          color="red"
          :loading="cancelling"
          @click="cancelOrder"
        >
          {{ $t('order.cancelOrder') }}
        </UButton>
        <UButton
          v-if="['shipped', 'completed'].includes(order.status)"
          variant="outline"
          color="orange"
          :loading="refunding"
          @click="requestRefund"
        >
          {{ $t('order.requestRefund') }}
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
definePageMeta({ middleware: 'auth-or-guest' })

const route   = useRoute()
const { t }   = useI18n()
const auth    = useAuthStore()
const api     = useApi()
const toast   = useToast()

useHead({ title: `Order Details — OPPLII` })

const { data: order, pending: loading, refresh } = await useAsyncData(
  `order-${route.params.id}`,
  () => api.getOrder(Number(route.params.id)) as Promise<any>
)

const cancelling = ref(false)
const refunding  = ref(false)
const registerLink = computed(() => {
  const email = auth.user?.email
  return email ? `/auth/register?email=${encodeURIComponent(email)}` : '/auth/register'
})

async function cancelOrder() {
  cancelling.value = true
  try {
    await api.cancelOrder(Number(route.params.id))
    toast.add({ title: 'Order cancelled', color: 'green' })
    await refresh()
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally {
    cancelling.value = false
  }
}

async function requestRefund() {
  refunding.value = true
  try {
    await api.requestRefund(Number(route.params.id))
    toast.add({ title: 'Refund requested', color: 'green' })
    await refresh()
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally {
    refunding.value = false
  }
}

function formatDate(d: string) { return dayjs(d).format('MMMM D, YYYY [at] h:mm A') }
</script>
