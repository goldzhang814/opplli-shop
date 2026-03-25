<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Inventory</h2>
    </div>
    <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true" style="margin-bottom:16px">
      <n-gi span="2 l:1">
        <n-card title="Low Stock Alert" :bordered="false" style="border-radius:14px">
          <n-data-table :columns="lowStockCols" :data="lowStock" :bordered="false" size="small" />
        </n-card>
      </n-gi>
      <n-gi span="2 l:1">
        <n-card title="Inventory Logs" :bordered="false" style="border-radius:14px">
          <n-data-table :columns="logCols" :data="logs" :bordered="false" size="small" />
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <n-pagination v-model:page="page" :item-count="total" :page-size="20" @update:page="loadLogs" />
          </div>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>
<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { NTag } from 'naive-ui'
import { api } from '@/composables/useApi'
import dayjs from 'dayjs'
const lowStock = ref<any[]>([])
const logs = ref<any[]>([])
const total = ref(0); const page = ref(1)
const lowStockCols = [
  { title: 'Product', key: 'product_name' },
  { title: 'SKU', key: 'sku_code', render: (r:any) => h('code', {style:'font-size:11px'}, r.sku_code) },
  { title: 'Stock', key: 'stock', render: (r:any) => h(NTag, { type: r.stock === 0 ? 'error' : 'warning', size:'small' }, () => String(r.stock)) },
  { title: 'Threshold', key: 'threshold' },
]
const logCols = [
  { title: 'SKU', key: 'sku_id', width: 60 },
  { title: 'Change', key: 'change_qty', render: (r:any) => h('span', { style: `color:${r.change_qty > 0 ? '#10b981' : '#ef4444'}; font-weight:600` }, (r.change_qty > 0 ? '+' : '') + r.change_qty) },
  { title: 'After', key: 'after_qty' },
  { title: 'Reason', key: 'reason', render: (r:any) => h(NTag, { size:'small' }, () => r.reason) },
  { title: 'Date', key: 'created_at', render: (r:any) => dayjs(r.created_at).format('MMM D HH:mm') },
]
async function loadLogs() {
  try { const { data } = await api.inventory({ page: page.value }); logs.value = data.items; total.value = data.total } catch { }
}
onMounted(async () => {
  const [low] = await Promise.all([api.lowStock(), loadLogs()])
  lowStock.value = low.data
})
</script>
<style scoped>
.page-header { display:flex;align-items:center;justify-content:space-between;margin-bottom:20px; }
.page-title { font-size:20px;font-weight:600;color:#18181b; }
</style>
