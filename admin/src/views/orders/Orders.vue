<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Orders</h2>
        <p class="page-sub">{{ total }} total orders</p>
      </div>
    </div>

    <!-- Filters -->
    <n-card :bordered="false" style="border-radius:14px; margin-bottom:16px">
      <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center">
        <n-input
          v-model:value="search"
          placeholder="Order no. or email…"
          clearable style="width:220px"
          @update:value="debouncedLoad"
        >
          <template #prefix><n-icon :component="SearchOutline" /></template>
        </n-input>

        <n-select
          v-model:value="statusFilter"
          :options="statusOptions"
          placeholder="All statuses"
          clearable
          style="width:180px"
          @update:value="load"
        />

        <n-select
          v-model:value="paymentFilter"
          :options="paymentOptions"
          placeholder="All payments"
          clearable
          style="width:160px"
          @update:value="load"
        />

        <n-button @click="load" :loading="loading">
          <template #icon><n-icon :component="RefreshOutline" /></template>
        </n-button>
      </div>
    </n-card>

    <n-card :bordered="false" style="border-radius:14px">
      <n-data-table
        :columns="columns"
        :data="orders"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        size="small"
        :row-key="(r: any) => r.id"
      />
      <div style="display:flex; justify-content:flex-end; margin-top:16px">
        <n-pagination
          v-model:page="page"
          :item-count="total"
          :page-size="20"
          @update:page="load"
        />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NTag, NButton, NIcon, NSpace, useMessage, useDialog } from 'naive-ui'
import { SearchOutline, RefreshOutline, EyeOutline, CarOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import { useDebounceFn } from '@vueuse/core'
import dayjs from 'dayjs'

const router  = useRouter()
const message = useMessage()
const dialog  = useDialog()

const orders  = ref<any[]>([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)
const search  = ref('')
const statusFilter  = ref<string | null>(null)
const paymentFilter = ref<string | null>(null)

const statusOptions = [
  { label: 'Pending Payment',  value: 'pending_payment' },
  { label: 'Processing',       value: 'pending_shipment' },
  { label: 'Shipped',          value: 'shipped' },
  { label: 'Completed',        value: 'completed' },
  { label: 'Cancelled',        value: 'cancelled' },
  { label: 'Refunded',         value: 'refunded' },
]

const paymentOptions = [
  { label: 'Stripe',    value: 'stripe' },
  { label: 'PayPal',    value: 'paypal' },
  { label: 'Airwallex', value: 'airwallex' },
]

const statusColor: Record<string, any> = {
  pending_payment:  'warning', pending_shipment: 'info',
  shipped: 'success', completed: 'success', cancelled: 'default', refunded: 'error',
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.orders({
      page: page.value,
      status: statusFilter.value || undefined,
      payment_method: paymentFilter.value || undefined,
      search: search.value || undefined,
    })
    orders.value = data.items
    total.value  = data.total
  } catch { /* silent */ }
  finally { loading.value = false }
}

const debouncedLoad = useDebounceFn(load, 400)
onMounted(load)

const columns = [
  {
    title: 'Order No.',
    key:   'order_no',
    render: (r: any) => h(
      'a',
      { style: 'color:#10b981; font-family:monospace; font-size:12px; cursor:pointer', onClick: () => router.push(`/orders/${r.id}`) },
      r.order_no
    ),
  },
  {
    title: 'Customer',
    key:   'guest_email',
    render: (r: any) => h('span', { style: 'font-size:12px; color:#6b7280' }, r.guest_email || `User #${r.user_id}`),
  },
  { title: 'Items', key: 'item_count', width: 70 },
  {
    title: 'Total',
    key:   'total_amount',
    render: (r: any) => h('span', { style: 'font-weight:600' }, `$${r.total_amount.toFixed(2)}`),
  },
  {
    title: 'Payment',
    key:   'payment_method',
    render: (r: any) => h('span', { style: 'text-transform:capitalize; font-size:12px' }, r.payment_method || '—'),
  },
  {
    title: 'Status',
    key:   'status',
    render: (r: any) => h(NTag, { type: statusColor[r.status] || 'default', size: 'small', round: true },
      () => r.status.replace(/_/g, ' ')),
  },
  {
    title: 'Date',
    key:   'created_at',
    render: (r: any) => h('span', { style: 'font-size:12px; color:#6b7280' }, dayjs(r.created_at).format('MMM D, HH:mm')),
  },
  {
    title: 'Actions',
    key:   '_actions',
    render: (r: any) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { size: 'tiny', quaternary: true, onClick: () => router.push(`/orders/${r.id}`) }, {
        default: () => h(NIcon, { component: EyeOutline }),
      }),
      r.status === 'pending_shipment'
        ? h(NButton, { size: 'tiny', type: 'primary', onClick: () => openShipDialog(r) }, {
            default: () => h(NIcon, { component: CarOutline }),
          })
        : null,
    ]),
  },
]

function openShipDialog(order: any) {
  let carrierId = ''
  let trackingNo = ''
  dialog.create({
    title: `Ship Order ${order.order_no}`,
    content: () => h('div', { style: 'display:flex; flex-direction:column; gap:12px; margin-top:12px' }, [
      h('input', { placeholder: 'Carrier ID (e.g. 1)', type: 'number', style: 'padding:8px; border:1px solid #e5e7eb; border-radius:8px; font-size:14px', onInput: (e: any) => carrierId = e.target.value }),
      h('input', { placeholder: 'Tracking Number', style: 'padding:8px; border:1px solid #e5e7eb; border-radius:8px; font-size:14px', onInput: (e: any) => trackingNo = e.target.value }),
    ]),
    positiveText: 'Mark Shipped',
    negativeText: 'Cancel',
    onPositiveClick: async () => {
      try {
        await api.shipOrder(order.id, { carrier_id: Number(carrierId), tracking_no: trackingNo })
        message.success('Order shipped!')
        load()
      } catch (e) { message.error(errMsg(e)) }
    },
  })
}
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
.page-sub    { font-size:13px; color:#9ca3af; margin-top:2px; }
</style>
