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
    <h1 class="font-head text-3xl font-bold text-zinc-900 mb-8">{{ $t('order.title') }}</h1>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-zinc-100 rounded-2xl animate-pulse" />
    </div>

    <div v-else-if="!orders.length" class="text-center py-16">
      <div class="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-shopping-bag" class="w-8 h-8 text-zinc-300" />
      </div>
      <p class="font-head font-semibold text-zinc-600 mb-4">{{ $t('order.empty') }}</p>
      <UButton to="/products">Shop Now</UButton>
    </div>

    <div v-else class="space-y-4">
      <NuxtLink
        v-for="order in orders"
        :key="order.id"
        :to="`/orders/${order.id}`"
        class="block bg-white border border-zinc-100 rounded-2xl p-5 hover:border-emerald-200 hover:shadow-sm transition-all"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="font-semibold text-zinc-900 font-mono text-sm">{{ $t('order.orderNo', { no: order.order_no }) }}</p>
            <p class="text-xs text-zinc-400 mt-0.5">{{ formatDate(order.created_at) }}</p>
          </div>
          <OrderStatusBadge :status="order.status" />
        </div>

        <div class="flex items-center justify-between mt-3">
          <p class="text-sm text-zinc-500">{{ order.item_count }} item{{ order.item_count !== 1 ? 's' : '' }}</p>
          <p class="font-head font-bold text-zinc-900">${{ order.total_amount.toFixed(2) }}</p>
        </div>
      </NuxtLink>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center mt-8">
      <UPagination v-model="page" :total="total" :page-count="10" />
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
definePageMeta({ middleware: 'auth-or-guest' })

const { t }    = useI18n()
const auth     = useAuthStore()
const api      = useApi()
const page     = ref(1)
const registerLink = computed(() => {
  const email = auth.user?.email
  return email ? `/auth/register?email=${encodeURIComponent(email)}` : '/auth/register'
})

useHead({ title: `My Orders — OPPLII` })

const { data, pending: loading } = await useAsyncData(
  'my-orders',
  () => api.listOrders(page.value) as Promise<any>,
  { watch: [page] }
)

const orders     = computed(() => data.value?.items ?? [])
const total      = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => data.value?.pages ?? 1)

function formatDate(d: string) { return dayjs(d).format('MMM D, YYYY') }
</script>
