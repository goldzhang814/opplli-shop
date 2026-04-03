<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">Shipping & Tax</h2>
    <n-tabs type="line" animated>

      <!-- Zones + Rules -->
      <n-tab-pane name="zones" tab="Zones & Rules">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <div v-for="zone in zones" :key="zone.id" style="margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #f3f4f6">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
              <span style="font-weight:600;font-size:15px;color:#18181b">{{ zone.name }}</span>
              <div style="display:flex;gap:4px;flex-wrap:wrap">
                <n-tag v-for="cc in zone.country_codes" :key="cc" size="small">{{ cc }}</n-tag>
              </div>
            </div>
            <div v-for="rule in zone.rules" :key="rule.id" style="display:flex;align-items:center;gap:16px;font-size:13px;background:#f9fafb;border-radius:10px;padding:10px 14px">
              <span style="color:#6b7280">Fee:</span><span style="font-weight:600">${{ rule.shipping_fee }}</span>
              <span style="color:#6b7280">Free shipping over:</span><span style="font-weight:600">${{ rule.free_shipping_threshold }}</span>
              <n-tag :type="rule.is_active?'success':'default'" size="small" round>{{ rule.is_active?'Active':'Off' }}</n-tag>
              <n-button size="tiny" @click="openRuleEdit(rule)">Edit</n-button>
            </div>
          </div>
          <p v-if="!zones.length" style="text-align:center;color:#9ca3af;padding:24px">Loading…</p>
        </n-card>
      </n-tab-pane>

      <!-- Carriers -->
      <n-tab-pane name="carriers" tab="Carriers">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openCarrierForm()">
            <template #icon><n-icon :component="AddOutline"/></template>Add Carrier
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <n-data-table :columns="carrierCols" :data="carriers" :bordered="false" size="small"/>
        </n-card>
      </n-tab-pane>

      <!-- Tax Rules -->
      <n-tab-pane name="tax" tab="Tax Rules">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openTaxForm()">
            <template #icon><n-icon :component="AddOutline"/></template>Add Tax Rule
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <n-data-table :columns="taxCols" :data="taxRules" :bordered="false" size="small"/>
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <!-- Rule edit modal -->
    <n-modal v-model:show="showRuleEdit" :mask-closable="false">
      <n-card style="width:420px;border-radius:14px" title="Edit Shipping Rule">
        <n-form label-placement="top" size="medium">
          <n-form-item label="Shipping Fee ($)">
            <n-input-number v-model:value="ruleForm.shipping_fee" :min="0" :precision="2" style="width:100%"/>
          </n-form-item>
          <n-form-item label="Free Shipping Threshold ($)">
            <n-input-number v-model:value="ruleForm.free_shipping_threshold" :min="0" :precision="2" style="width:100%"/>
          </n-form-item>
          <n-form-item label="Active"><n-switch v-model:value="ruleForm.is_active"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showRuleEdit=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveRule">Save</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Carrier modal -->
    <n-modal v-model:show="showCarrierForm" :mask-closable="false">
      <n-card style="width:480px;border-radius:14px" :title="editCarrierId?'Edit Carrier':'New Carrier'">
        <n-form label-placement="top" size="medium">
          <n-form-item label="Name *"><n-input v-model:value="cf.name" placeholder="UPS"/></n-form-item>
          <n-form-item label="Code *"><n-input v-model:value="cf.code" placeholder="ups"/></n-form-item>
          <n-form-item label="Tracking URL Template">
            <n-input v-model:value="cf.tracking_url_template" placeholder="https://ups.com/track?tracknum={tracking_no}"/>
          </n-form-item>
          <n-form-item label="Active"><n-switch v-model:value="cf.is_active"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showCarrierForm=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveCarrier">{{ editCarrierId?'Save':'Create' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Tax modal -->
    <n-modal v-model:show="showTaxForm" :mask-closable="false">
      <n-card style="width:480px;border-radius:14px" :title="editTaxId?'Edit Tax Rule':'New Tax Rule'">
        <n-form label-placement="top" size="medium">
          <n-grid :cols="2" :x-gap="12">
            <n-gi>
              <n-form-item label="Country Code *">
                <n-select
                  v-model:value="tf.country_code"
                  :options="countryOptions"
                  placeholder="Select country"
                  clearable
                />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="State Code">
                <n-select
                  v-model:value="tf.state_code"
                  :options="stateSelectOptions"
                  placeholder="All states (country-wide)"
                  clearable
                />
              </n-form-item>
            </n-gi>
            <n-gi><n-form-item label="Tax Rate (%) *"><n-input-number v-model:value="tf.tax_rate" :min="0" :max="100" :precision="2" style="width:100%"/></n-form-item></n-gi>
            <n-gi><n-form-item label="Tax Name"><n-input v-model:value="tf.tax_name" placeholder="Sales Tax"/></n-form-item></n-gi>
          </n-grid>
          <n-form-item label="Apply to Shipping"><n-switch v-model:value="tf.apply_to_shipping"/></n-form-item>
          <n-form-item label="Active"><n-switch v-model:value="tf.is_active"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showTaxForm=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveTax">{{ editTaxId?'Save':'Create' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h, watch } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'

const message = useMessage()
const saving  = ref(false)

const zones           = ref<any[]>([])
const carriers        = ref<any[]>([])
const taxRules        = ref<any[]>([])
const shippingRegions = ref<any[]>([])
const countryOptions  = ref<{ label: string; value: string }[]>([])
const stateOptions    = ref<string[]>([])
const stateCache      = reactive<Record<string, string[]>>({})

const stateSelectOptions = computed(() => [
  { label: 'All states (country-wide)', value: '' },
  ...stateOptions.value.map(code => ({ label: code, value: code })),
])

const loadAll = async () => {
  try {
    const [z, c, t, r] = await Promise.all([
      api.shippingZones(),
      api.carriers(),
      api.taxRules(),
      api.shippingRegions(),
    ])
    zones.value = z.data
    carriers.value = c.data
    taxRules.value = t.data
    shippingRegions.value = Array.isArray(r.data) ? r.data : []
    updateCountryOptions()
  } catch {}
}

function updateCountryOptions() {
  const countrySet = new Set<string>()
  zones.value.forEach(z => {
    (z.country_codes || []).forEach((cc: string) => {
      if (cc) countrySet.add(cc.toUpperCase())
    })
  })
  shippingRegions.value.forEach(region => {
    if (region?.country_code) {
      countrySet.add(region.country_code.toUpperCase())
    }
  })
  countryOptions.value = [...countrySet]
    .filter(Boolean)
    .sort()
    .map(code => ({ label: code, value: code }))
}

async function ensureRegionsLoaded() {
  if (shippingRegions.value.length) return
  try {
    const { data } = await api.shippingRegions()
    shippingRegions.value = Array.isArray(data) ? data : []
    updateCountryOptions()
  } catch {}
}

async function loadStates(country?: string) {
  const upper = country?.toUpperCase?.()
  if (!upper) {
    stateOptions.value = []
    return
  }
  await ensureRegionsLoaded()
  if (stateCache[upper]) {
    stateOptions.value = stateCache[upper]
    return
  }
  const states = Array.from(
    new Set(
      shippingRegions.value
        .filter(region => (region.country_code?.toUpperCase() ?? '') === upper && region.state_code)
        .map(region => (region.state_code as string).toUpperCase())
    )
  )
  stateCache[upper] = states
  stateOptions.value = states
}

// Rule edit
const showRuleEdit = ref(false); const editRuleId = ref<number|null>(null)
const ruleForm = reactive({ shipping_fee: 0, free_shipping_threshold: 0, is_active: true })
function openRuleEdit(r: any) { editRuleId.value = r.id; Object.assign(ruleForm, { shipping_fee: r.shipping_fee, free_shipping_threshold: r.free_shipping_threshold, is_active: r.is_active }); showRuleEdit.value = true }
async function saveRule() { saving.value=true; try { await api.updateRule(editRuleId.value!, ruleForm); message.success('Saved'); showRuleEdit.value=false; loadAll() } catch(e){message.error(errMsg(e))} finally{saving.value=false} }

// Carriers
const showCarrierForm = ref(false); const editCarrierId = ref<number|null>(null)
const cf = reactive({ name:'', code:'', tracking_url_template:'', is_active:true })
function openCarrierForm(c?: any) { editCarrierId.value=c?.id??null; Object.assign(cf, c?{name:c.name,code:c.code,tracking_url_template:c.tracking_url_template||'',is_active:c.is_active}:{name:'',code:'',tracking_url_template:'',is_active:true}); showCarrierForm.value=true }
async function saveCarrier() { saving.value=true; try { editCarrierId.value?await api.updateCarrier(editCarrierId.value,cf):await api.createCarrier(cf); message.success('Saved'); showCarrierForm.value=false; loadAll() } catch(e){message.error(errMsg(e))} finally{saving.value=false} }

const carrierCols = [
  { title:'Name', key:'name' },
  { title:'Code', key:'code', render:(r:any)=>h('code',{style:'font-size:11px;background:#f3f4f6;padding:2px 5px;border-radius:4px'},r.code) },
  { title:'Tracking URL', key:'tracking_url_template', render:(r:any)=>h('span',{style:'font-size:11px;color:#6b7280'},r.tracking_url_template||'—'), ellipsis:{tooltip:true} },
  { title:'Status', key:'is_active', render:(r:any)=>h(NTag,{type:r.is_active?'success':'default',size:'small',round:true},()=>r.is_active?'Active':'Off'), width:80 },
  { title:'', key:'_e', width:60, render:(r:any)=>h(NButton,{size:'tiny',quaternary:true,onClick:()=>openCarrierForm(r)},{default:()=>h(NIcon,{component:CreateOutline})}) },
]

// Tax rules
const showTaxForm = ref(false); const editTaxId = ref<number|null>(null)
const tf = reactive({ country_code:'', state_code:'', tax_rate:0, tax_name:'Sales Tax', apply_to_shipping:false, is_active:true })

watch(() => tf.country_code, (newVal) => {
  if (!newVal) {
    stateOptions.value = []
    return
  }
  const upper = newVal.toUpperCase()
  if (upper !== newVal) {
    tf.country_code = upper
    return
  }
  loadStates(upper)
})
async function openTaxForm(t?: any) {
  editTaxId.value = t?.id ?? null
  Object.assign(tf, t ? {
    country_code: t.country_code,
    state_code: t.state_code || '',
    tax_rate: parseFloat(t.tax_rate) * 100,
    tax_name: t.tax_name,
    apply_to_shipping: t.apply_to_shipping,
    is_active: t.is_active,
  } : {
    country_code: '',
    state_code: '',
    tax_rate: 0,
    tax_name: 'Sales Tax',
    apply_to_shipping: false,
    is_active: true,
  })
  await loadStates(tf.country_code)
  showTaxForm.value = true
}
async function saveTax() {
  saving.value = true
  const payload = {
    ...tf,
    tax_rate: tf.tax_rate / 100,
    state_code: tf.state_code || undefined,
  }
  try {
    if (editTaxId.value) {
      await api.updateTax(editTaxId.value, payload)
    } else {
      await api.createTax(payload)
    }
    message.success('Saved')
    showTaxForm.value = false
    loadAll()
  } catch (e) {
    message.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

const taxCols = [
  { title:'Country', key:'country_code', width:90 },
  { title:'State',   key:'state_code', render:(r:any)=>r.state_code||'All', width:80 },
  { title:'Rate',    key:'tax_rate', render:(r:any)=>`${(parseFloat(r.tax_rate)*100).toFixed(2)}%`, width:80 },
  { title:'Name',    key:'tax_name' },
  { title:'On Ship', key:'apply_to_shipping', render:(r:any)=>h(NTag,{type:r.apply_to_shipping?'info':'default',size:'small'},()=>r.apply_to_shipping?'Yes':'No'), width:80 },
  { title:'Status',  key:'is_active', render:(r:any)=>h(NTag,{type:r.is_active?'success':'default',size:'small',round:true},()=>r.is_active?'Active':'Off'), width:70 },
  { title:'', key:'_a', width:80, render:(r:any)=>h(NSpace,{size:'small'},()=>[
    h(NButton,{size:'tiny',quaternary:true,onClick:()=>openTaxForm(r)},{default:()=>h(NIcon,{component:CreateOutline})}),
    h(NButton,{size:'tiny',quaternary:true,type:'error',onClick:async()=>{try{await api.deleteTax(r.id);loadAll()}catch(e){message.error(errMsg(e))}}},{default:()=>h(NIcon,{component:TrashOutline})}),
  ]) },
]

onMounted(loadAll)
</script>
<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }
</style>
