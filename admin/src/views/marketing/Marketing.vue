<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">Marketing</h2>
    <n-tabs type="line" animated>

      <!-- Banners tab -->
      <n-tab-pane name="banners" tab="Banners">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openBannerForm()">
            <template #icon><n-icon :component="AddOutline"/></template>New Banner
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <div v-for="b in banners" :key="b.id"
            style="display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid #f3f4f6;last:border-0">
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-weight:500;font-size:14px">{{ b.title }}</span>
                <n-tag :type="b.is_active?'success':'default'" size="small" round>{{ b.is_active?'Active':'Off' }}</n-tag>
              </div>
              <p v-if="b.subtitle" style="font-size:12px;color:#6b7280;margin-top:2px">{{ b.subtitle }}</p>
              <p style="font-size:11px;color:#9ca3af;margin-top:2px">
                {{ b.starts_at ? dayjs(b.starts_at).format('MMM D') : '∞' }} → {{ b.ends_at ? dayjs(b.ends_at).format('MMM D, YYYY') : '∞' }}
              </p>
            </div>
            <n-space>
              <n-button size="small" quaternary @click="openBannerForm(b)"><n-icon :component="CreateOutline"/></n-button>
              <n-button size="small" quaternary type="error" @click="delBanner(b.id)"><n-icon :component="TrashOutline"/></n-button>
            </n-space>
          </div>
          <p v-if="!banners.length" style="text-align:center;color:#9ca3af;padding:24px">No banners yet</p>
        </n-card>
      </n-tab-pane>

      <!-- Newsletter tab -->
      <n-tab-pane name="newsletter" tab="Newsletter">
        <n-grid :cols="3" :x-gap="12" style="margin:16px 0 20px">
          <n-gi><n-card :bordered="false" style="border-radius:14px"><n-statistic label="Total" :value="nlStats.total||0"/></n-card></n-gi>
          <n-gi><n-card :bordered="false" style="border-radius:14px"><n-statistic label="Active" :value="nlStats.active||0"/></n-card></n-gi>
          <n-gi><n-card :bordered="false" style="border-radius:14px"><n-statistic label="Unsubscribed" :value="nlStats.unsubscribed||0"/></n-card></n-gi>
        </n-grid>
        <div style="display:flex;justify-content:flex-end;margin-bottom:12px">
          <n-button @click="exportCsv"><template #icon><n-icon :component="DownloadOutline"/></template>Export CSV</n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <n-data-table :columns="nlCols" :data="subscribers" :bordered="false" size="small" :loading="nlLoading"/>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <n-pagination v-model:page="nlPage" :item-count="nlTotal" :page-size="50" @update:page="loadNl"/>
          </div>
        </n-card>
      </n-tab-pane>

      <!-- Channels tab -->
      <n-tab-pane name="channels" tab="Channels">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openChForm()">
            <template #icon><n-icon :component="AddOutline"/></template>New Channel
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <n-data-table :columns="chCols" :data="channels" :bordered="false" size="small"/>
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <!-- Banner modal -->
    <n-modal v-model:show="showBannerForm" :mask-closable="false">
      <n-card style="width:480px;border-radius:14px" :title="editBannerId?'Edit Banner':'New Banner'">
        <n-form :model="bf" label-placement="top" size="medium">
          <n-form-item label="Title *"><n-input v-model:value="bf.title"/></n-form-item>
          <n-form-item label="Subtitle"><n-input v-model:value="bf.subtitle"/></n-form-item>
          <n-form-item label="Link URL"><n-input v-model:value="bf.link_url" placeholder="https://..."/></n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-gi><n-form-item label="Starts At"><n-date-picker v-model:value="bf.starts_at" type="datetime" clearable style="width:100%"/></n-form-item></n-gi>
            <n-gi><n-form-item label="Ends At"><n-date-picker v-model:value="bf.ends_at" type="datetime" clearable style="width:100%"/></n-form-item></n-gi>
          </n-grid>
          <n-form-item label="Active"><n-switch v-model:value="bf.is_active"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showBannerForm=false">Cancel</n-button>
          <n-button type="primary" :loading="savingBanner" @click="saveBanner">{{ editBannerId?'Save':'Create' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Channel modal -->
    <n-modal v-model:show="showChForm" :mask-closable="false">
      <n-card style="width:400px;border-radius:14px" :title="editChId?'Edit Channel':'New Channel'">
        <n-form :model="cf" label-placement="top" size="medium">
          <n-form-item label="Name *"><n-input v-model:value="cf.name"/></n-form-item>
          <n-form-item label="Ref Code *"><n-input v-model:value="cf.ref_code" placeholder="instagram"/></n-form-item>
          <n-form-item label="Platform"><n-input v-model:value="cf.platform" placeholder="instagram, tiktok…"/></n-form-item>
          <n-form-item label="Active"><n-switch v-model:value="cf.is_active"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showChForm=false">Cancel</n-button>
          <n-button type="primary" :loading="savingCh" @click="saveCh">{{ editChId?'Save':'Create' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline, DownloadOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import dayjs from 'dayjs'

const message = useMessage()

// ── Banners ──────────────────────────────────────────────────────────────────
const banners       = ref<any[]>([])
const showBannerForm= ref(false)
const editBannerId  = ref<number|null>(null)
const savingBanner  = ref(false)
const bf            = reactive({ title:'', subtitle:'', link_url:'', starts_at: null as any, ends_at: null as any, is_active: true })

const loadBanners   = async () => { try { banners.value = (await api.banners()).data } catch {} }

function openBannerForm(b?: any) {
  editBannerId.value = b?.id ?? null
  Object.assign(bf, b
    ? { title: b.title, subtitle: b.subtitle||'', link_url: b.link_url||'', is_active: b.is_active,
        starts_at: b.starts_at ? new Date(b.starts_at).getTime() : null,
        ends_at:   b.ends_at   ? new Date(b.ends_at).getTime()   : null }
    : { title:'', subtitle:'', link_url:'', starts_at:null, ends_at:null, is_active:true })
  showBannerForm.value = true
}

async function saveBanner() {
  savingBanner.value = true
  const p = { ...bf,
    starts_at: bf.starts_at ? new Date(bf.starts_at).toISOString() : null,
    ends_at:   bf.ends_at   ? new Date(bf.ends_at).toISOString()   : null }
  try {
    editBannerId.value ? await api.updateBanner(editBannerId.value, p) : await api.createBanner(p)
    message.success('Saved'); showBannerForm.value = false; loadBanners()
  } catch (e) { message.error(errMsg(e)) }
  finally { savingBanner.value = false }
}

async function delBanner(id: number) {
  try { await api.deleteBanner(id); message.success('Deleted'); loadBanners() }
  catch (e) { message.error(errMsg(e)) }
}

// ── Newsletter ────────────────────────────────────────────────────────────────
const subscribers = ref<any[]>([])
const nlStats     = ref<any>({})
const nlTotal     = ref(0); const nlPage = ref(1); const nlLoading = ref(false)

async function loadNl() {
  nlLoading.value = true
  try {
    const [list, stats] = await Promise.all([api.newsletter({ page: nlPage.value }), api.newsletterStats()])
    subscribers.value = list.data.items; nlTotal.value = list.data.total; nlStats.value = stats.data
  } catch {} finally { nlLoading.value = false }
}

async function exportCsv() {
  try {
    const { data } = await api.newsletterExport()
    const url = URL.createObjectURL(data as Blob)
    const a   = Object.assign(document.createElement('a'), { href: url, download: `subscribers-${dayjs().format('YYYY-MM-DD')}.csv` })
    a.click(); URL.revokeObjectURL(url)
  } catch (e) { message.error(errMsg(e)) }
}

const nlCols = [
  { title:'Email',  key:'email' },
  { title:'Source', key:'source', render:(r:any)=>h(NTag,{size:'small'},()=>r.source), width:110 },
  { title:'Status', key:'status', render:(r:any)=>h(NTag,{type:r.status==='active'?'success':'default',size:'small',round:true},()=>r.status), width:100 },
  { title:'Date',   key:'subscribed_at', render:(r:any)=>dayjs(r.subscribed_at).format('MMM D, YYYY'), width:130 },
  { title:'', key:'_d', width:50, render:(r:any)=>h(NButton,{size:'tiny',quaternary:true,type:'error',onClick:async()=>{try{await api.deleteSubscriber(r.id);loadNl()}catch{}}},{default:()=>h(NIcon,{component:TrashOutline})}) },
]

// ── Channels ──────────────────────────────────────────────────────────────────
const channels    = ref<any[]>([])
const showChForm  = ref(false)
const editChId    = ref<number|null>(null)
const savingCh    = ref(false)
const cf          = reactive({ name:'', ref_code:'', platform:'', is_active:true })

const loadChannels = async () => { try { channels.value = (await api.channels()).data } catch {} }

function openChForm(c?: any) {
  editChId.value = c?.id ?? null
  Object.assign(cf, c ? { name:c.name, ref_code:c.ref_code, platform:c.platform||'', is_active:c.is_active } : { name:'', ref_code:'', platform:'', is_active:true })
  showChForm.value = true
}

async function saveCh() {
  savingCh.value = true
  try {
    editChId.value ? await api.updateChannel(editChId.value, cf) : await api.createChannel(cf)
    message.success('Saved'); showChForm.value = false; loadChannels()
  } catch (e) { message.error(errMsg(e)) }
  finally { savingCh.value = false }
}

const chCols = [
  { title:'Name',     key:'name' },
  { title:'Ref Code', key:'ref_code', render:(r:any)=>h('code',{style:'background:#f0fdf4;color:#059669;padding:2px 6px;border-radius:4px;font-size:11px'},r.ref_code) },
  { title:'Platform', key:'platform', render:(r:any)=>r.platform||'—' },
  { title:'Status',   key:'is_active', render:(r:any)=>h(NTag,{type:r.is_active?'success':'default',size:'small',round:true},()=>r.is_active?'Active':'Off'), width:80 },
  { title:'',key:'_e',width:60,render:(r:any)=>h(NButton,{size:'tiny',quaternary:true,onClick:()=>openChForm(r)},{default:()=>h(NIcon,{component:CreateOutline})}) },
]

onMounted(() => { loadBanners(); loadNl(); loadChannels() })
</script>
<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }
</style>
