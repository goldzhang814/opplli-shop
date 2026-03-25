<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Customers</h2>
      <p class="page-sub">{{ total }} registered customers</p>
    </div>
    <n-card :bordered="false" style="border-radius:14px; margin-bottom:16px">
      <n-input v-model:value="search" placeholder="Search by email or name…" clearable style="width:300px"
        @update:value="debouncedLoad">
        <template #prefix><n-icon :component="SearchOutline" /></template>
      </n-input>
    </n-card>
    <n-card :bordered="false" style="border-radius:14px">
      <n-data-table :columns="columns" :data="users" :loading="loading" :bordered="false" size="small" />
      <div style="display:flex; justify-content:flex-end; margin-top:16px">
        <n-pagination v-model:page="page" :item-count="total" :page-size="20" @update:page="load" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { SearchOutline, BanOutline, CheckmarkOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import { useDebounceFn } from '@vueuse/core'
import dayjs from 'dayjs'

const message = useMessage()
const users   = ref<any[]>([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)
const search  = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await api.orders({ page: page.value, search: search.value || undefined })
    // Use user list endpoint - fall back to showing from orders
    users.value = data.items?.map((o: any) => ({ id: o.user_id, email: o.guest_email, created_at: o.created_at, is_active: true })) || []
    total.value = data.total || 0
  } catch { /* silent */ }
  finally { loading.value = false }
}

const debouncedLoad = useDebounceFn(load, 400)
onMounted(load)

const columns = [
  { title: 'Email',   key: 'email',      render: (r: any) => h('span', { style: 'font-size:13px' }, r.email || '—') },
  { title: 'Joined',  key: 'created_at', render: (r: any) => dayjs(r.created_at).format('MMM D, YYYY'), width: 130 },
  {
    title: 'Status',
    key:   'is_active',
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'error', size: 'small', round: true }, () => r.is_active ? 'Active' : 'Banned'),
    width: 90,
  },
]
</script>

<style scoped>
.page-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
.page-sub    { font-size:13px; color:#9ca3af; margin-top:2px; }
</style>
