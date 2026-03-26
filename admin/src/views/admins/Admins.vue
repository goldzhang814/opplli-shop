<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Admin Users</h2>
      <n-button type="primary" @click="openForm()">
        <template #icon><n-icon :component="AddOutline"/></template>New Admin
      </n-button>
    </div>

    <n-card :bordered="false" style="border-radius:14px">
      <n-data-table :columns="columns" :data="admins" :loading="loading" :bordered="false" size="small"/>
    </n-card>

    <!-- Create admin modal -->
    <n-modal v-model:show="showForm" :mask-closable="false">
      <n-card style="width:440px;border-radius:14px" title="New Admin">
        <n-form :model="form" label-placement="top" size="medium">
          <n-form-item label="Email *"><n-input v-model:value="form.email" type="email"/></n-form-item>
          <n-form-item label="Password *"><n-input v-model:value="form.password" type="password"/></n-form-item>
          <n-form-item label="Full Name"><n-input v-model:value="form.full_name"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showForm=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="create">Create</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Permissions modal -->
    <n-modal v-model:show="showPerms" :mask-closable="false">
      <n-card style="width:520px;border-radius:14px" :title="`Permissions: ${permTarget?.email}`">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px">
          <div v-for="mod in modules" :key="mod" style="display:flex;align-items:center;justify-content:space-between;background:#f9fafb;border-radius:8px;padding:8px 12px">
            <span style="font-size:13px;text-transform:capitalize">{{ mod.replace(/_/g,' ') }}</span>
            <n-switch :value="perms[mod]" @update:value="(v: boolean) => perms[mod] = v" size="small"/>
          </div>
        </div>
        <n-space justify="end">
          <n-button @click="showPerms=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="savePerms">Save Permissions</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { AddOutline, KeyOutline, ToggleOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const message = useMessage()
const auth    = useAuthStore()
const admins  = ref<any[]>([])
const loading = ref(false)
const saving  = ref(false)
const showForm= ref(false)
const showPerms = ref(false)
const permTarget= ref<any>(null)
const perms     = reactive<Record<string,boolean>>({})
const form      = reactive({ email:'', password:'', full_name:'' })

const modules = [
  'products','categories','inventory','reviews',
  'orders','payments','coupons','banners',
  'newsletter','channels','shipping','tax',
  'carriers','content','seo','email_templates',
  'statistics','admins',
]

async function load() {
  loading.value = true
  try { admins.value = (await api.admins()).data } catch {} finally { loading.value = false }
}

async function create() {
  saving.value = true
  try { await api.createAdmin(form); message.success('Admin created'); showForm.value=false; load() }
  catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

function openPerms(a: any) {
  permTarget.value = a
  modules.forEach((m: string) => { perms[m] = !!a.permissions?.[m] })
  showPerms.value = true
}

async function savePerms() {
  saving.value = true
  try {
    await api.updatePermissions(permTarget.value.id, { permissions: { ...perms } })
    message.success('Permissions updated'); showPerms.value=false; load()
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

async function toggleStatus(a: any) {
  if (a.role === 'super_admin') { message.warning('Cannot disable super admin'); return }
  try { await api.toggleAdminStatus(a.id); load() }
  catch (e) { message.error(errMsg(e)) }
}

function openForm() { Object.assign(form, {email:'',password:'',full_name:''}); showForm.value=true }

const columns = [
  { title:'Email',   key:'email' },
  { title:'Name',    key:'full_name', render:(r:any)=>r.full_name||'—' },
  { title:'Role',    key:'role', render:(r:any)=>h(NTag,{type:r.role==='super_admin'?'error':'default',size:'small',round:true},()=>r.role.replace(/_/g,' ')), width:120 },
  { title:'Status',  key:'is_active', render:(r:any)=>h(NTag,{type:r.is_active?'success':'error',size:'small',round:true},()=>r.is_active?'Active':'Disabled'), width:90 },
  { title:'Last Login', key:'last_login_at', render:(r:any)=>r.last_login_at?dayjs(r.last_login_at).format('MMM D, HH:mm'):'Never', width:130 },
  {
    title:'Actions', key:'_a', width:100,
    render:(r:any)=>h(NSpace,{size:'small'},()=>[
      h(NButton,{size:'tiny',quaternary:true,disabled:r.role==='super_admin',onClick:()=>openPerms(r)},{default:()=>h(NIcon,{component:KeyOutline})}),
      r.id !== auth.admin?.id && r.role !== 'super_admin'
        ? h(NButton,{size:'tiny',quaternary:true,type:r.is_active?'warning':'success',onClick:()=>toggleStatus(r)},{default:()=>h(NIcon,{component:ToggleOutline})})
        : null,
    ]),
  },
]

onMounted(load)
</script>
<style scoped>
.page-header { display:flex;align-items:center;justify-content:space-between;margin-bottom:20px; }
.page-title  { font-size:20px;font-weight:600;color:#18181b; }
</style>
