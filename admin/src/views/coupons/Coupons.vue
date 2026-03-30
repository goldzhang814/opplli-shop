<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Coupons</h2>
      <n-button type="primary" @click="openForm()">
        <template #icon><n-icon :component="AddOutline" /></template>
        Create Coupon
      </n-button>
    </div>

    <n-card :bordered="false" style="border-radius:14px">
      <n-data-table :columns="columns" :data="coupons" :loading="loading" :bordered="false" size="small" />
    </n-card>

    <!-- Form modal -->
    <n-modal v-model:show="showForm" :mask-closable="false">
      <n-card style="width:520px; border-radius:14px" :title="editing ? 'Edit Coupon' : 'Create Coupon'">
        <n-form :model="form" label-placement="top" size="medium">
          <n-grid :cols="2" :x-gap="12">
            <n-gi span="2">
              <n-form-item label="Code *">
                <n-input v-model:value="form.code" placeholder="SAVE20" style="text-transform:uppercase" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Type *">
                <n-select v-model:value="form.type" :options="typeOptions" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item :label="form.type === 'percent' ? 'Discount (%)' : 'Discount ($)'">
                <n-input-number v-model:value="form.value" :min="0" :disabled="form.type === 'free_shipping'" style="width:100%" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Min. Order ($)">
                <n-input-number v-model:value="form.min_order_amount" :min="0" placeholder="No minimum" style="width:100%" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Max Uses">
                <n-input-number v-model:value="form.max_uses" :min="1" placeholder="Unlimited" style="width:100%" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Starts At">
                <n-date-picker v-model:value="form.starts_at" type="datetime" clearable style="width:100%" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Ends At">
                <n-date-picker v-model:value="form.ends_at" type="datetime" clearable style="width:100%" />
              </n-form-item>
            </n-gi>
            <n-gi span="2">
              <n-form-item label="Active">
                <n-switch v-model:value="form.is_active" />
              </n-form-item>
            </n-gi>
          </n-grid>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showForm = false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="save">
            {{ editing ? 'Save Changes' : 'Create' }}
          </n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, NSwitch, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import dayjs from 'dayjs'

const message = useMessage()
const coupons = ref<any[]>([])
const loading = ref(false)
const showForm= ref(false)
const editing = ref<number | null>(null)
const saving  = ref(false)

const form = reactive({
  code: '', type: 'percent', value: 10,
  min_order_amount: null as number | null, max_uses: null as number | null,
  starts_at: null as number | null, ends_at: null as number | null, is_active: true,
})

const typeOptions = [
  { label: 'Percentage (%)', value: 'percent' },
  { label: 'Fixed ($)',      value: 'fixed' },
  { label: 'Free Shipping',  value: 'free_shipping' },
]

async function load() {
  loading.value = true
  try { const { data } = await api.coupons(); coupons.value = data }
  catch { /* silent */ }
  finally { loading.value = false }
}

onMounted(load)

function openForm(c?: any) {
  if (c) {
    editing.value = c.id
    Object.assign(form, {
      code: c.code, type: c.type, value: c.value,
      min_order_amount: c.min_order_amount, max_uses: c.max_uses,
      starts_at: c.starts_at ? new Date(c.starts_at).getTime() : null,
      ends_at:   c.ends_at   ? new Date(c.ends_at).getTime()   : null,
      is_active: c.is_active,
    })
  } else {
    editing.value = null
    Object.assign(form, { code: '', type: 'percent', value: 10, min_order_amount: null, max_uses: null, starts_at: null, ends_at: null, is_active: true })
  }
  showForm.value = true
}

async function save() {
  saving.value = true
  const payload = {
    ...form,
    code: form.code.toUpperCase(),
    starts_at: form.starts_at ? new Date(form.starts_at).toISOString() : null,
    ends_at:   form.ends_at   ? new Date(form.ends_at).toISOString()   : null,
  }
  try {
    editing.value ? await api.updateCoupon(editing.value, payload) : await api.createCoupon(payload)
    message.success(editing.value ? 'Updated' : 'Created')
    showForm.value = false
    load()
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

async function deleteCoupon(id: number) {
  try { await api.deleteCoupon(id); message.success('Deleted'); load() }
  catch (e) { message.error(errMsg(e)) }
}

const columns = [
  { title: 'Id', key: 'id', width: 120 },
  {
    title: 'Code',
    key: 'code',
    render: (r: any) => h('code', { style: 'background:#f0fdf4; color:#059669; padding:2px 8px; border-radius:6px; font-size:12px; font-weight:700' }, r.code),
  width: 150},
  { title: 'Type', key: 'type', render: (r: any) => r.type.replace(/_/g, ' '), width: 120 },
  {
    title: 'Value',
    key: 'value',
    render: (r: any) => r.type === 'percent' ? `${r.value}%` : r.type === 'fixed' ? `$${r.value}` : 'Free ship',
    width: 150,
  },
  { title: 'Min Order', key: 'min_order_amount', render: (r: any) => r.min_order_amount ? `$${r.min_order_amount}` : '—', width: 100 },
  {
    title: 'Usage',
    key: 'used_count',
    render: (r: any) => `${r.used_count} / ${r.max_uses ?? '∞'}`,
    width: 150,
  },
  {
    title: 'Expires',
    key: 'ends_at',
    render: (r: any) => r.ends_at ? dayjs(r.ends_at).format('MMM D, YYYY') : 'Never',
    width: 150,
  },
  {
    title: 'Active',
    key: 'is_active',
    render: (r: any) => h(NTag, { type: r.is_active ? 'success' : 'default', size: 'small', round: true }, () => r.is_active ? 'Active' : 'Off'),
    width: 150,
  },
  {
    title: 'Actions',
    key: '_a',
    width: 150,
    render: (r: any) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { size: 'tiny', quaternary: true, onClick: () => openForm(r) }, { default: () => h(NIcon, { component: CreateOutline }) }),
      h(NButton, { size: 'tiny', quaternary: true, type: 'error', onClick: () => deleteCoupon(r.id) }, { default: () => h(NIcon, { component: TrashOutline }) }),
    ]),
  },
]
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
</style>
