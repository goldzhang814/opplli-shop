<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Dashboard</h2>
        <p class="page-sub">{{ today }}</p>
      </div>
      <n-button @click="load" :loading="loading">
        <template #icon><n-icon :component="RefreshOutline" /></template>
        Refresh
      </n-button>
    </div>

    <!-- KPI cards -->
    <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true" style="margin-bottom:16px">
      <n-gi v-for="kpi in kpis" :key="kpi.label" span="2 m:1 l:1" style="display:flex">
        <n-card :bordered="false" style="flex:1; border-radius:14px">
          <div class="kpi-card">
            <div class="kpi-icon" :style="{ background: kpi.bg }">
              <n-icon :component="kpi.icon" size="20" :color="kpi.color" />
            </div>
            <div>
              <p class="kpi-label">{{ kpi.label }}</p>
              <p class="kpi-value">{{ kpi.value }}</p>
              <p v-if="kpi.sub" class="kpi-sub">{{ kpi.sub }}</p>
            </div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Action required -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true" style="margin-bottom:16px">
      <n-gi v-for="a in alerts" :key="a.label" span="4 m:2 l:1">
        <n-card :bordered="false" style="border-radius:14px">
          <div class="alert-card">
            <n-badge :value="a.count" :color="a.color" :max="999">
              <div class="alert-icon" :style="{ background: a.bg }">
                <n-icon :component="a.icon" size="18" :color="a.color" />
              </div>
            </n-badge>
            <p class="alert-label">{{ a.label }}</p>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- Charts row -->
    <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
      <!-- Revenue chart -->
      <n-gi span="3 l:2">
        <n-card title="Revenue (Last 30 Days)" :bordered="false" style="border-radius:14px">
          <v-chart :option="revenueChart" autoresize style="height:240px" />
        </n-card>
      </n-gi>

      <!-- Top products -->
      <n-gi span="3 l:1">
        <n-card title="Top Products (30d)" :bordered="false" style="border-radius:14px">
          <div class="top-products">
            <div v-for="(p, i) in topProducts" :key="p.product_id" class="top-product-row">
              <span class="top-rank">{{ i + 1 }}</span>
              <div class="top-info">
                <p class="top-name">{{ p.product_name }}</p>
                <p class="top-units">{{ p.units_sold }} units</p>
              </div>
              <span class="top-rev">${{ p.revenue.toFixed(0) }}</span>
            </div>
            <p v-if="!topProducts.length" class="empty-hint">No data yet</p>
          </div>
        </n-card>
      </n-gi>

      <!-- Recent orders -->
      <n-gi span="3">
        <n-card title="Recent Orders" :bordered="false" style="border-radius:14px">
          <n-data-table :columns="orderCols" :data="recentOrders" :bordered="false" size="small" />
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { RouterLink } from 'vue-router'
import { NTag, NButton, NIcon } from 'naive-ui'
import { use } from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import {
  CashOutline, CartOutline, PeopleOutline, TimeOutline,
  MailOutline, StarOutline, RefreshOutline, TrendingUpOutline
} from '@vicons/ionicons5'
import { api } from '@/composables/useApi'
import dayjs from 'dayjs'

use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const loading    = ref(false)
const stats      = ref<any>({})
const topProducts= ref<any[]>([])
const recentOrders = ref<any[]>([])
const revByDay   = ref<any[]>([])

const today = dayjs().format('dddd, MMMM D, YYYY')

async function load() {
  loading.value = true
  try {
    const { data } = await api.dashboard()
    stats.value       = data.stats
    topProducts.value = data.top_products
    recentOrders.value= data.recent_orders
    revByDay.value    = data.revenue_by_day
  } catch { /* silent */ }
  finally { loading.value = false }
}

onMounted(load)

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)

const kpis = computed(() => [
  { label: 'GMV Today',      value: fmt(stats.value.gmv_today || 0),      sub: `This month: ${fmt(stats.value.gmv_this_month || 0)}`, icon: CashOutline,     bg: '#ecfdf5', color: '#10b981' },
  { label: 'Orders Today',   value: stats.value.orders_today || 0,        sub: `This month: ${stats.value.orders_this_month || 0}`,   icon: CartOutline,     bg: '#eff6ff', color: '#3b82f6' },
  { label: 'New Users Today',value: stats.value.new_users_today || 0,     sub: `Total: ${stats.value.total_users || 0}`,              icon: PeopleOutline,   bg: '#f5f3ff', color: '#8b5cf6' },
  { label: 'All-Time GMV',   value: fmt(stats.value.gmv_total || 0),      sub: `Last month: ${fmt(stats.value.gmv_last_month || 0)}`, icon: TrendingUpOutline, bg: '#fff7ed', color: '#f97316' },
])

const alerts = computed(() => [
  { label: 'Pending Payment',  count: stats.value.orders_pending_payment  || 0, icon: TimeOutline,  bg: '#fefce8', color: '#eab308' },
  { label: 'Ready to Ship',    count: stats.value.orders_pending_shipment || 0, icon: CartOutline,  bg: '#eff6ff', color: '#3b82f6' },
  { label: 'Pending Reviews',  count: stats.value.pending_reviews || 0,        icon: StarOutline,  bg: '#fefce8', color: '#eab308' },
  { label: 'This Month Orders',count: stats.value.orders_this_month || 0,      icon: MailOutline,  bg: '#ecfdf5', color: '#10b981' },
])

const revenueChart = computed(() => ({
  grid:    { top: 20, left: 50, right: 20, bottom: 30 },
  xAxis:   {
    type:       'category',
    data:       revByDay.value.map(d => dayjs(d.date).format('MMM D')),
    axisLine:   { show: false },
    axisTick:   { show: false },
    axisLabel:  { color: '#9ca3af', fontSize: 11, interval: 4 },
  },
  yAxis:   {
    type:       'value',
    axisLabel:  { color: '#9ca3af', fontSize: 11, formatter: (v: number) => `$${v >= 1000 ? (v/1000).toFixed(0)+'k' : v}` },
    splitLine:  { lineStyle: { color: '#f3f4f6' } },
    axisLine:   { show: false },
  },
  tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].name}<br/>$${p[0].value.toFixed(2)}` },
  series:  [{
    type:      'line', smooth: true, symbol: 'none',
    data:      revByDay.value.map(d => d.revenue),
    lineStyle: { color: '#10b981', width: 2.5 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16,185,129,0.2)' }, { offset: 1, color: 'rgba(16,185,129,0)' }] } },
  }],
}))

const statusColor: Record<string, string> = {
  pending_payment:  'warning', pending_shipment: 'info', shipped: 'success',
  completed: 'success', cancelled: 'default', refunded: 'error',
}

const orderCols = [
  { title: 'Order No.',  key: 'order_no', render: (r: any) => h(RouterLink, { to: `/orders/${r.id}`, style: 'color:#10b981; font-family:monospace; font-size:13px' }, () => r.order_no) },
  { title: 'Status',     key: 'status',   render: (r: any) => h(NTag, { type: (statusColor[r.status] || 'default') as any, size: 'small', round: true }, () => r.status.replace(/_/g, ' ')) },
  { title: 'Total',      key: 'total_amount', render: (r: any) => `$${r.total_amount.toFixed(2)}` },
  { title: 'Date',       key: 'created_at',  render: (r: any) => dayjs(r.created_at).format('MMM D, HH:mm') },
]
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
.page-sub    { font-size:13px; color:#9ca3af; margin-top:2px; }

.kpi-card   { display:flex; align-items:center; gap:14px; }
.kpi-icon   { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.kpi-label  { font-size:12px; color:#6b7280; text-transform:uppercase; letter-spacing:0.04em; font-weight:500; }
.kpi-value  { font-size:24px; font-weight:700; color:#18181b; line-height:1.2; }
.kpi-sub    { font-size:12px; color:#9ca3af; margin-top:2px; }

.alert-card  { display:flex; flex-direction:column; align-items:center; gap:10px; padding:8px 0; text-align:center; }
.alert-icon  { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; }
.alert-label { font-size:12px; color:#6b7280; font-weight:500; }

.top-products { display:flex; flex-direction:column; gap:12px; padding-top:4px; }
.top-product-row { display:flex; align-items:center; gap:10px; }
.top-rank   { width:20px; text-align:center; font-size:13px; font-weight:700; color:#d1d5db; }
.top-info   { flex:1; min-width:0; }
.top-name   { font-size:13px; font-weight:500; color:#374151; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.top-units  { font-size:11px; color:#9ca3af; }
.top-rev    { font-size:13px; font-weight:600; color:#18181b; flex-shrink:0; }
.empty-hint { font-size:13px; color:#9ca3af; text-align:center; padding:16px 0; }
</style>
