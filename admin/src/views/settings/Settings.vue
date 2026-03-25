<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">Settings</h2>

    <n-tabs type="line" animated>
      <!-- SEO -->
      <n-tab-pane name="seo" tab="SEO">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <n-form :model="seo" label-placement="top" size="medium" style="max-width:700px">
            <n-form-item label="Site Name">
              <n-input v-model:value="seo.site_name" />
            </n-form-item>
            <n-form-item label="Default Meta Title">
              <n-input v-model:value="seo.meta_title" />
            </n-form-item>
            <n-form-item label="Default Meta Description">
              <n-input v-model:value="seo.meta_description" type="textarea" :rows="3" />
            </n-form-item>
            <n-form-item label="Google Analytics ID">
              <n-input v-model:value="seo.google_analytics_id" placeholder="G-XXXXXXXXXX" />
            </n-form-item>
            <n-form-item label="Default OG Image URL">
              <n-input v-model:value="seo.og_image" placeholder="https://..." />
            </n-form-item>
            <n-form-item label="Robots.txt">
              <n-input v-model:value="seo.robots_txt" type="textarea" :rows="5" style="font-family:monospace; font-size:12px" />
            </n-form-item>
            <n-button type="primary" :loading="savingSeo" @click="saveSeo">Save SEO Settings</n-button>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- General -->
      <n-tab-pane name="general" tab="General">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <div style="max-width:700px; display:flex; flex-direction:column; gap:12px">
            <div
              v-for="s in settings"
              :key="s.key"
              style="border:1px solid #e5e7eb; border-radius:12px; padding:16px; display:flex; align-items:center; gap:16px"
            >
              <div style="flex:1; min-width:0">
                <code style="font-size:12px; background:#f0fdf4; color:#059669; padding:2px 6px; border-radius:4px">{{ s.key }}</code>
                <p v-if="s.description" style="font-size:12px; color:#9ca3af; margin-top:4px">{{ s.description }}</p>
                <n-input
                  :value="s.value || ''"
                  @update:value="v => updateSettingLocal(s.key, v)"
                  size="small"
                  style="margin-top:8px"
                />
              </div>
              <n-button
                size="small"
                type="primary"
                :loading="savingKey === s.key"
                @click="saveSetting(s.key)"
              >
                Save
              </n-button>
            </div>
          </div>
        </n-card>
      </n-tab-pane>

      <!-- Contact -->
      <n-tab-pane name="contact" tab="Contact Info">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <n-form label-placement="top" size="medium" style="max-width:560px">
            <n-form-item v-for="c in contactFields" :key="c.key" :label="c.label">
              <n-input
                :value="contactValues[c.key] || ''"
                @update:value="v => contactValues[c.key] = v"
                :placeholder="c.placeholder"
              />
            </n-form-item>
            <n-button type="primary" :loading="savingContact" @click="saveContact">
              Save Contact Info
            </n-button>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- Review threshold -->
      <n-tab-pane name="reviews" tab="Reviews">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px; max-width:500px">
          <n-form label-placement="top">
            <n-form-item label="Auto-approve threshold (stars)">
              <n-input-number v-model:value="reviewThreshold" :min="0" :max="5" />
            </n-form-item>
            <p style="font-size:12px; color:#9ca3af; margin-bottom:16px">
              Reviews with {{ reviewThreshold }} or more stars are auto-approved. Set to 0 for all manual review.
            </p>
            <n-button type="primary" @click="saveReviewThreshold">Save</n-button>
          </n-form>
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { api, errMsg } from '@/composables/useApi'

const message = useMessage()

// SEO
const seo       = reactive<Record<string, string>>({})
const savingSeo = ref(false)

async function loadSeo() {
  try { const { data } = await api.seo(); Object.assign(seo, data) } catch { /* silent */ }
}

async function saveSeo() {
  savingSeo.value = true
  try { await api.updateSeo({ ...seo }); message.success('SEO settings saved') }
  catch (e) { message.error(errMsg(e)) }
  finally { savingSeo.value = false }
}

// General settings
const settings      = ref<any[]>([])
const settingDraft  = reactive<Record<string, string>>({})
const savingKey     = ref<string | null>(null)

async function loadSettings() {
  try { const { data } = await api.settings(); settings.value = data } catch { /* silent */ }
}

function updateSettingLocal(key: string, val: string) {
  const s = settings.value.find(x => x.key === key)
  if (s) s.value = val
}

async function saveSetting(key: string) {
  const s = settings.value.find(x => x.key === key)
  if (!s) return
  savingKey.value = key
  try { await api.updateSetting(key, s.value || ''); message.success('Saved') }
  catch (e) { message.error(errMsg(e)) }
  finally { savingKey.value = null }
}

// Contact
const contactValues  = reactive<Record<string, string>>({})
const savingContact  = ref(false)
const contactFields  = [
  { key: 'contact_email',     label: 'Support Email',  placeholder: 'support@example.com' },
  { key: 'contact_whatsapp',  label: 'WhatsApp',       placeholder: '+1234567890' },
  { key: 'contact_facebook',  label: 'Facebook URL',   placeholder: 'https://facebook.com/...' },
  { key: 'contact_telegram',  label: 'Telegram',       placeholder: '@username or https://t.me/...' },
]

async function saveContact() {
  savingContact.value = true
  try {
    for (const f of contactFields) {
      if (contactValues[f.key] !== undefined) {
        await api.updateSetting(f.key, contactValues[f.key])
      }
    }
    message.success('Contact info saved')
  } catch (e) { message.error(errMsg(e)) }
  finally { savingContact.value = false }
}

// Review threshold
const reviewThreshold = ref(3)
async function saveReviewThreshold() {
  try {
    await api.updateSetting('review_auto_approve_threshold', String(reviewThreshold.value))
    message.success('Saved')
  } catch (e) { message.error(errMsg(e)) }
}

onMounted(async () => {
  await Promise.all([loadSeo(), loadSettings()])
  // Populate contact values
  for (const f of contactFields) {
    const s = settings.value.find(x => x.key === f.key)
    if (s) contactValues[f.key] = s.value || ''
  }
  const threshold = settings.value.find(s => s.key === 'review_auto_approve_threshold')
  if (threshold) reviewThreshold.value = Number(threshold.value) || 3
})
</script>

<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }
</style>
