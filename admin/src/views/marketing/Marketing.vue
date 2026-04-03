<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">Marketing</h2>
    <n-tabs type="line" animated>

      <!-- ── Banners ───────────────────────────────────────────────────── -->
      <n-tab-pane name="banners" tab="Banners">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openBannerForm()">
            <template #icon><n-icon :component="AddOutline"/></template>New Banner
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <div v-for="b in banners" :key="b.id"
            style="display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid #f3f4f6">
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-weight:500;font-size:14px">{{ b.title }}</span>
                <n-tag :type="b.is_active?'success':'default'" size="small" round>{{ b.is_active?'Active':'Off' }}</n-tag>
              </div>
              <p v-if="b.subtitle" style="font-size:12px;color:#6b7280;margin-top:2px">{{ b.subtitle }}</p>
              <p style="font-size:11px;color:#9ca3af;margin-top:2px">
                {{ b.starts_at ? dayjs(b.starts_at).format('MMM D') : '∞' }} →
                {{ b.ends_at ? dayjs(b.ends_at).format('MMM D, YYYY') : '∞' }}
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

      <!-- ── Newsletter ─────────────────────────────────────────────────── -->
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

      <!-- ── Channels ───────────────────────────────────────────────────── -->
      <n-tab-pane name="channels" tab="Channels">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openChForm()">
            <template #icon><n-icon :component="AddOutline"/></template>New Channel
          </n-button>
        </div>

        <!-- Channel cards with stats -->
        <div v-if="chLoading" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px">
          <div v-for="i in 3" :key="i" style="height:200px;background:#f3f4f6;border-radius:14px;animation:pulse 1.5s infinite"/>
        </div>

        <div v-else-if="!channels.length" style="text-align:center;padding:40px;color:#9ca3af">
          No channels yet. Create one to start tracking.
        </div>

        <div v-else style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;margin-bottom:20px">
          <n-card
            v-for="ch in channels" :key="ch.id"
            :bordered="false"
            style="border-radius:14px;cursor:pointer;transition:box-shadow 0.2s"
            :style="selectedChannel?.id === ch.id ? 'box-shadow:0 0 0 2px #10b981' : ''"
            @click="selectChannel(ch)"
          >
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px">
              <div>
                <div style="display:flex;align-items:center;gap:8px">
                  <span style="font-weight:600;font-size:15px;color:#18181b">{{ ch.name }}</span>
                  <n-tag :type="ch.is_active?'success':'default'" size="small" round>{{ ch.is_active?'Active':'Off' }}</n-tag>
                </div>
                <code style="font-size:11px;background:#f0fdf4;color:#059669;padding:2px 6px;border-radius:4px;margin-top:4px;display:inline-block">
                  ?ref={{ ch.ref_code }}
                </code>
              </div>
              <div style="display:flex;gap:6px">
                <n-button size="tiny" quaternary @click.stop="openChForm(ch)"><n-icon :component="CreateOutline"/></n-button>
                <n-button size="tiny" quaternary type="primary" @click.stop="copyLink(ch)" title="Copy promo link">
                  <n-icon :component="LinkOutline"/>
                </n-button>
              </div>
            </div>

            <!-- Funnel stats -->
            <div v-if="ch._stats" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center">
              <div class="funnel-stat">
                <p class="funnel-val">{{ fmt(ch._stats.visit_count) }}</p>
                <p class="funnel-lbl">Visits</p>
              </div>
              <div class="funnel-stat">
                <p class="funnel-val">{{ fmt(ch._stats.add_to_cart_count) }}</p>
                <p class="funnel-lbl">Add to Cart</p>
                <p class="funnel-rate" v-if="ch._stats.visit_count">
                  {{ rate(ch._stats.add_to_cart_count, ch._stats.visit_count) }}
                </p>
              </div>
              <div class="funnel-stat">
                <p class="funnel-val">{{ fmt(ch._stats.order_count) }}</p>
                <p class="funnel-lbl">Orders</p>
                <p class="funnel-rate" v-if="ch._stats.visit_count">
                  {{ rate(ch._stats.order_count, ch._stats.visit_count) }}
                </p>
              </div>
              <div class="funnel-stat">
                <p class="funnel-val" style="color:#10b981">${{ fmtMoney(ch._stats.total_revenue) }}</p>
                <p class="funnel-lbl">Revenue</p>
              </div>
            </div>
            <div v-else style="text-align:center;padding:16px 0;color:#d1d5db;font-size:13px">
              Click to load stats
            </div>

            <!-- Funnel bar chart -->
            <div v-if="ch._stats && ch._stats.visit_count > 0" style="margin-top:12px">
              <div
                v-for="bar in funnelBars(ch._stats)"
                :key="bar.label"
                style="margin-bottom:6px"
              >
                <div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280;margin-bottom:2px">
                  <span>{{ bar.label }}</span>
                  <span>{{ bar.pct }}%</span>
                </div>
                <div style="height:6px;background:#f3f4f6;border-radius:999px;overflow:hidden">
                  <div
                    :style="`width:${bar.pct}%;background:${bar.color};height:100%;border-radius:999px;transition:width 0.6s ease`"
                  />
                </div>
              </div>
            </div>
          </n-card>
        </div>

        <!-- Link Generator panel -->
        <n-card v-if="channels.length" :bordered="false" style="border-radius:14px">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
            <n-icon :component="LinkOutline" style="color:#10b981" size="18"/>
            <span style="font-weight:600;font-size:15px;color:#18181b">Promo Link Generator</span>
          </div>

          <n-form label-placement="left" label-width="110" size="medium">
            <n-grid :cols="2" :x-gap="16">
              <n-gi>
                <n-form-item label="Channel">
                  <n-select
                    v-model:value="linkGen.channelId"
                    :options="channelOptions"
                    placeholder="Select channel"
                    @update:value="onLinkChannelChange"
                  />
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="Page">
                  <n-select
                    v-model:value="linkGen.page"
                    :options="pageOptions"
                    placeholder="Select target page"
                  />
                </n-form-item>
              </n-gi>
              <n-gi v-if="linkGen.page === 'product'">
                <n-form-item label="Product Slug">
                  <n-input v-model:value="linkGen.slug" placeholder="e.g. wart-corn-remover-pads"/>
                </n-form-item>
              </n-gi>
              <n-gi v-if="linkGen.page === 'custom'">
                <n-form-item label="Custom Path">
                  <n-input v-model:value="linkGen.customPath" placeholder="/pages/sale"/>
                </n-form-item>
              </n-gi>
            </n-grid>
          </n-form>

          <!-- Generated links -->
          <div v-if="generatedLinks.length" style="margin-top:4px">
            <p style="font-size:12px;font-weight:500;color:#6b7280;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.04em">Generated Links</p>
            <div
              v-for="link in generatedLinks" :key="link.label"
              style="display:flex;align-items:center;gap:10px;background:#f9fafb;border-radius:10px;padding:10px 14px;margin-bottom:8px"
            >
              <div style="flex:1;min-width:0">
                <p style="font-size:11px;color:#9ca3af;font-weight:500;margin-bottom:2px">{{ link.label }}</p>
                <p style="font-size:13px;color:#374151;word-break:break-all;font-family:monospace">{{ link.url }}</p>
              </div>
              <n-button size="small" @click="copyUrl(link.url)">
                <template #icon><n-icon :component="CopyOutline"/></template>
                Copy
              </n-button>
            </div>
          </div>

          <div v-else-if="linkGen.channelId" style="text-align:center;color:#9ca3af;padding:16px;font-size:13px">
            Select a page to generate links
          </div>
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
      <n-card style="width:440px;border-radius:14px" :title="editChId?'Edit Channel':'New Channel'">
        <n-form :model="cf" label-placement="top" size="medium">
          <n-form-item label="Channel Name *"><n-input v-model:value="cf.name" placeholder="Instagram KOL"/></n-form-item>
          <n-form-item label="Ref Code *">
            <n-input v-model:value="cf.ref_code" placeholder="instagram_kol01"/>
            <template #feedback>Used in ?ref= URL parameter. Lowercase, no spaces.</template>
          </n-form-item>
          <n-form-item label="Platform">
            <n-select v-model:value="cf.platform" :options="platformOptions" clearable placeholder="Select platform"/>
          </n-form-item>
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
import { ref, reactive, computed, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage, useNotification } from 'naive-ui'
import {
  AddOutline, CreateOutline, TrashOutline,
  DownloadOutline, LinkOutline, CopyOutline,
} from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import dayjs from 'dayjs'

const message      = useMessage()
const notification = useNotification()

// ── Store URL (from env or fallback) ──────────────────────────────────────────
const STORE_URL = import.meta.env.VITE_STORE_URL || 'https://yourstore.com'

// ── Helpers ───────────────────────────────────────────────────────────────────
const fmt      = (n: number) => n >= 1000 ? `${(n/1000).toFixed(1)}k` : String(n)
const fmtMoney = (n: number) => n >= 1000 ? `${(n/1000).toFixed(1)}k` : n.toFixed(0)
const rate     = (a: number, b: number) => b ? `${((a/b)*100).toFixed(1)}%` : '0%'

function funnelBars(stats: any) {
  const v = stats.visit_count || 1
  return [
    { label: 'Visit → Cart',  pct: Math.round((stats.add_to_cart_count / v) * 100), color: '#60a5fa' },
    { label: 'Visit → Order', pct: Math.round((stats.order_count       / v) * 100), color: '#10b981' },
  ]
}

// ── Banners ───────────────────────────────────────────────────────────────────
const banners       = ref<any[]>([])
const showBannerForm= ref(false)
const editBannerId  = ref<number|null>(null)
const savingBanner  = ref(false)
const bf            = reactive({ title:'', subtitle:'', link_url:'', starts_at: null as any, ends_at: null as any, is_active: true })

const loadBanners   = async () => { try { banners.value = (await api.banners()).data } catch {} }

function openBannerForm(b?: any) {
  editBannerId.value = b?.id ?? null
  Object.assign(bf, b
    ? { title:b.title, subtitle:b.subtitle||'', link_url:b.link_url||'', is_active:b.is_active,
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
  try { await api.deleteBanner(id); loadBanners() } catch (e) { message.error(errMsg(e)) }
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
  { title:'', key:'_d', width:50,
    render:(r:any)=>h(NButton,{size:'tiny',quaternary:true,type:'error',
      onClick:async()=>{try{await api.deleteSubscriber(r.id);loadNl()}catch{}}
    },{default:()=>h(NIcon,{component:TrashOutline})}) },
]

// ── Channels ──────────────────────────────────────────────────────────────────
const channels       = ref<any[]>([])
const chLoading      = ref(false)
const selectedChannel= ref<any>(null)
const showChForm     = ref(false)
const editChId       = ref<number|null>(null)
const savingCh       = ref(false)
const cf             = reactive({ name:'', ref_code:'', platform:'', is_active:true })

const platformOptions = [
  { label:'Instagram', value:'instagram' },
  { label:'TikTok',    value:'tiktok' },
  { label:'Facebook',  value:'facebook' },
  { label:'YouTube',   value:'youtube' },
  { label:'Twitter/X', value:'twitter' },
  { label:'Google',    value:'google' },
  { label:'Email',     value:'email' },
  { label:'Other',     value:'other' },
]

async function loadChannels() {
  chLoading.value = true
  try {
    const { data } = await api.channels()
    channels.value = data.map((c: any) => ({ ...c, _stats: null }))
    // Load stats for all channels in parallel
    await Promise.all(channels.value.map(loadChannelStats))
  } catch {} finally { chLoading.value = false }
}

async function loadChannelStats(ch: any) {
  try {
    const { data } = await api.channelStats(ch.id)
    ch._stats = data
  } catch {}
}

async function selectChannel(ch: any) {
  selectedChannel.value = ch
  if (!ch._stats) await loadChannelStats(ch)
  // Pre-select in link generator
  linkGen.channelId = ch.id
  onLinkChannelChange(ch.id)
}

function openChForm(c?: any) {
  editChId.value = c?.id ?? null
  Object.assign(cf, c
    ? { name:c.name, ref_code:c.ref_code, platform:c.platform||'', is_active:c.is_active }
    : { name:'', ref_code:'', platform:'', is_active:true })
  showChForm.value = true
}

async function saveCh() {
  if (!cf.name || !cf.ref_code) { message.warning('Name and Ref Code are required'); return }
  savingCh.value = true
  try {
    editChId.value ? await api.updateChannel(editChId.value, cf) : await api.createChannel(cf)
    message.success('Saved'); showChForm.value = false; loadChannels()
  } catch (e) { message.error(errMsg(e)) }
  finally { savingCh.value = false }
}

function copyLink(ch: any) {
  const url = `${STORE_URL}/?ref=${ch.ref_code}`
  navigator.clipboard.writeText(url).then(() => {
    message.success(`Link copied: ${url}`)
  })
}

// ── Link Generator ────────────────────────────────────────────────────────────
const linkGen = reactive({
  channelId:  null as number | null,
  refCode:    '',
  page:       '' as string,
  slug:       '',
  customPath: '',
})

const pageOptions = [
  { label: '🏠 Homepage',          value: 'home' },
  { label: '🛍️  All Products',     value: 'products' },
  { label: '📦 Specific Product', value: 'product' },
  { label: '📝 Blog',              value: 'blog' },
  { label: '❓ FAQ',               value: 'faq' },
  { label: '🔗 Custom Path',       value: 'custom' },
]

const channelOptions = computed(() =>
  channels.value.map(c => ({ label: `${c.name} (${c.ref_code})`, value: c.id }))
)

function onLinkChannelChange(id: number) {
  const ch = channels.value.find(c => c.id === id)
  linkGen.refCode = ch?.ref_code || ''
}

const generatedLinks = computed(() => {
  if (!linkGen.channelId || !linkGen.refCode || !linkGen.page) return []
  const ref = `?ref=${linkGen.refCode}`

  let basePath = ''
  if (linkGen.page === 'home')     basePath = '/'
  if (linkGen.page === 'products') basePath = '/products'
  if (linkGen.page === 'blog')     basePath = '/blog'
  if (linkGen.page === 'faq')      basePath = '/faq'
  if (linkGen.page === 'product')  basePath = `/products/${linkGen.slug || '[product-slug]'}`
  if (linkGen.page === 'custom')   basePath = linkGen.customPath || '/[path]'

  const base = `${STORE_URL}${basePath}${ref}`

  return [
    { label: 'Full URL', url: base },
    { label: 'With UTM (Google Analytics)', url: `${base}&utm_source=${linkGen.refCode}&utm_medium=referral&utm_campaign=${linkGen.refCode}` },
  ]
})

function copyUrl(url: string) {
  navigator.clipboard.writeText(url).then(() => {
    message.success('Copied to clipboard!')
  })
}

onMounted(() => { loadBanners(); loadNl(); loadChannels() })
</script>

<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }

.funnel-stat {
  background: #f9fafb;
  border-radius: 10px;
  padding: 10px 6px;
  text-align: center;
}
.funnel-val {
  font-size: 18px;
  font-weight: 700;
  color: #18181b;
  line-height: 1.2;
}
.funnel-lbl {
  font-size: 10px;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-top: 2px;
}
.funnel-rate {
  font-size: 11px;
  color: #10b981;
  font-weight: 500;
  margin-top: 2px;
}
</style>
