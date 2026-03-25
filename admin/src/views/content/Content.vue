<template>
  <div>
    <h2 class="page-title" style="margin-bottom:20px">Content</h2>
    <n-tabs type="line" animated>

      <!-- Blog Posts -->
      <n-tab-pane name="blog" tab="Blog">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openPostForm()">
            <template #icon><n-icon :component="AddOutline"/></template>New Post
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <n-data-table :columns="postCols" :data="posts" :loading="postsLoading" :bordered="false" size="small"/>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <n-pagination v-model:page="postsPage" :item-count="postsTotal" :page-size="20" @update:page="loadPosts"/>
          </div>
        </n-card>
      </n-tab-pane>

      <!-- FAQ -->
      <n-tab-pane name="faq" tab="FAQ">
        <div style="display:flex;justify-content:flex-end;margin:16px 0">
          <n-button type="primary" @click="openFaqForm()">
            <template #icon><n-icon :component="AddOutline"/></template>Add FAQ
          </n-button>
        </div>
        <n-card :bordered="false" style="border-radius:14px">
          <div v-for="f in faqs" :key="f.id" style="padding:14px 0;border-bottom:1px solid #f3f4f6">
            <div style="display:flex;align-items:flex-start;gap:12px">
              <div style="flex:1">
                <p style="font-weight:500;font-size:13px;color:#18181b;margin-bottom:4px">{{ f.question }}</p>
                <p style="font-size:12px;color:#6b7280;line-clamp:2">{{ f.answer?.substring(0,120) }}{{ f.answer?.length > 120 ? '…' : '' }}</p>
                <n-tag v-if="f.category" size="small" style="margin-top:6px">{{ f.category }}</n-tag>
              </div>
              <n-space>
                <n-button size="small" quaternary @click="openFaqForm(f)"><n-icon :component="CreateOutline"/></n-button>
                <n-button size="small" quaternary type="error" @click="delFaq(f.id)"><n-icon :component="TrashOutline"/></n-button>
              </n-space>
            </div>
          </div>
          <p v-if="!faqs.length" style="text-align:center;color:#9ca3af;padding:24px">No FAQs yet</p>
        </n-card>
      </n-tab-pane>

      <!-- CMS Pages -->
      <n-tab-pane name="cms" tab="Pages">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <div v-for="p in cmsPages" :key="`${p.page_type}-${p.language_code}`"
            style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid #f3f4f6">
            <div style="flex:1">
              <span style="font-weight:500;font-size:13px;text-transform:capitalize">{{ p.page_type.replace(/_/g,' ') }}</span>
              <n-tag size="small" style="margin-left:8px">{{ p.language_code.toUpperCase() }}</n-tag>
            </div>
            <n-button size="small" @click="openCmsEdit(p)"><n-icon :component="CreateOutline"/>&nbsp;Edit</n-button>
          </div>
        </n-card>
      </n-tab-pane>

      <!-- Email Templates -->
      <n-tab-pane name="email" tab="Email Templates">
        <n-card :bordered="false" style="border-radius:14px; margin-top:16px">
          <div v-for="t in emailTemplates" :key="`${t.type}-${t.language_code}`"
            style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid #f3f4f6">
            <div style="flex:1">
              <code style="font-size:12px;background:#f3f4f6;padding:2px 6px;border-radius:4px">{{ t.type }}</code>
              <n-tag size="small" style="margin-left:8px">{{ t.language_code.toUpperCase() }}</n-tag>
              <p style="font-size:12px;color:#6b7280;margin-top:2px">{{ t.subject }}</p>
            </div>
            <n-button size="small" @click="openTemplateEdit(t)"><n-icon :component="CreateOutline"/>&nbsp;Edit</n-button>
          </div>
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <!-- Blog post modal -->
    <n-modal v-model:show="showPostForm" :mask-closable="false">
      <n-card style="width:600px;border-radius:14px" :title="editPostId?'Edit Post':'New Post'">
        <n-form :model="pf" label-placement="top" size="medium">
          <n-form-item label="Title *"><n-input v-model:value="pf.title"/></n-form-item>
          <n-form-item label="Slug"><n-input v-model:value="pf.slug" placeholder="auto-generated from title"/></n-form-item>
          <n-form-item label="Excerpt"><n-input v-model:value="pf.excerpt" type="textarea" :rows="2"/></n-form-item>
          <n-form-item label="Author"><n-input v-model:value="pf.author"/></n-form-item>
          <n-form-item label="Published"><n-switch v-model:value="pf.is_published"/></n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showPostForm=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="savePost">{{ editPostId?'Save':'Create' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- FAQ modal -->
    <n-modal v-model:show="showFaqForm" :mask-closable="false">
      <n-card style="width:520px;border-radius:14px" :title="editFaqId?'Edit FAQ':'Add FAQ'">
        <n-form :model="ff" label-placement="top" size="medium">
          <n-form-item label="Question *"><n-input v-model:value="ff.question"/></n-form-item>
          <n-form-item label="Answer *"><n-input v-model:value="ff.answer" type="textarea" :rows="4"/></n-form-item>
          <n-grid :cols="2" :x-gap="12">
            <n-gi><n-form-item label="Category"><n-input v-model:value="ff.category" placeholder="General"/></n-form-item></n-gi>
            <n-gi><n-form-item label="Sort Order"><n-input-number v-model:value="ff.sort_order" :min="0" style="width:100%"/></n-form-item></n-gi>
          </n-grid>
          <n-form-item label="Language">
            <n-select v-model:value="ff.language_code" :options="[{label:'English',value:'en'},{label:'Español',value:'es'}]"/>
          </n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showFaqForm=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveFaq">{{ editFaqId?'Save':'Add' }}</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- CMS edit modal -->
    <n-modal v-model:show="showCmsEdit" :mask-closable="false">
      <n-card style="width:680px;border-radius:14px" :title="`Edit: ${cmsTarget?.page_type} (${cmsTarget?.language_code?.toUpperCase()})`">
        <n-form label-placement="top" size="medium">
          <n-form-item label="Title"><n-input v-model:value="cmsForm.title"/></n-form-item>
          <n-form-item label="Content (HTML)">
            <n-input v-model:value="cmsForm.content" type="textarea" :rows="12" style="font-family:monospace;font-size:12px"/>
          </n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showCmsEdit=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveCms">Save</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Email template modal -->
    <n-modal v-model:show="showTemplateEdit" :mask-closable="false">
      <n-card style="width:680px;border-radius:14px" :title="`Template: ${tmplTarget?.type} (${tmplTarget?.language_code?.toUpperCase()})`">
        <n-form label-placement="top" size="medium">
          <n-form-item label="Subject *"><n-input v-model:value="tmplForm.subject"/></n-form-item>
          <n-form-item label="Body (HTML)">
            <n-input v-model:value="tmplForm.body" type="textarea" :rows="12" style="font-family:monospace;font-size:12px"/>
          </n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showTemplateEdit=false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="saveTemplate">Save Template</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import dayjs from 'dayjs'

const message = useMessage()
const saving  = ref(false)

// ── Blog ──────────────────────────────────────────────────────────────────────
const posts       = ref<any[]>([])
const postsTotal  = ref(0); const postsPage = ref(1); const postsLoading = ref(false)
const showPostForm= ref(false); const editPostId = ref<number|null>(null)
const pf          = reactive({ title:'', slug:'', excerpt:'', author:'', is_published: false })

async function loadPosts() {
  postsLoading.value = true
  try { const { data } = await api.blogPosts({ page: postsPage.value }); posts.value = data.items; postsTotal.value = data.total }
  catch {} finally { postsLoading.value = false }
}

function openPostForm(p?: any) {
  editPostId.value = p?.id ?? null
  Object.assign(pf, p ? { title:p.title, slug:p.slug, excerpt:p.excerpt||'', author:p.author||'', is_published:p.is_published } : { title:'', slug:'', excerpt:'', author:'', is_published:false })
  showPostForm.value = true
}

async function savePost() {
  saving.value = true
  try {
    editPostId.value ? await api.updatePost(editPostId.value, pf) : await api.createPost(pf)
    message.success('Saved'); showPostForm.value = false; loadPosts()
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

const postCols = [
  { title:'Title', key:'title', render:(r:any)=>h('span',{style:'font-size:13px;font-weight:500'},r.title) },
  { title:'Author', key:'author', render:(r:any)=>r.author||'—', width:120 },
  { title:'Status', key:'is_published', render:(r:any)=>h(NTag,{type:r.is_published?'success':'default',size:'small',round:true},()=>r.is_published?'Published':'Draft'), width:100 },
  { title:'Date', key:'published_at', render:(r:any)=>r.published_at?dayjs(r.published_at).format('MMM D, YYYY'):'—', width:130 },
  { title:'', key:'_a', width:80, render:(r:any)=>h(NSpace,{size:'small'},()=>[
    h(NButton,{size:'tiny',quaternary:true,onClick:()=>openPostForm(r)},{default:()=>h(NIcon,{component:CreateOutline})}),
    h(NButton,{size:'tiny',quaternary:true,type:'error',onClick:async()=>{try{await api.deletePost(r.id);loadPosts()}catch(e){message.error(errMsg(e))}}},{default:()=>h(NIcon,{component:TrashOutline})}),
  ])},
]

// ── FAQ ───────────────────────────────────────────────────────────────────────
const faqs        = ref<any[]>([])
const showFaqForm = ref(false); const editFaqId = ref<number|null>(null)
const ff          = reactive({ question:'', answer:'', category:'', sort_order:0, language_code:'en' })

const loadFaqs    = async () => { try { faqs.value = (await api.faqs()).data } catch {} }

function openFaqForm(f?: any) {
  editFaqId.value = f?.id ?? null
  Object.assign(ff, f ? { question:f.question, answer:f.answer, category:f.category||'', sort_order:f.sort_order||0, language_code:f.language_code } : { question:'', answer:'', category:'', sort_order:0, language_code:'en' })
  showFaqForm.value = true
}

async function saveFaq() {
  saving.value = true
  try {
    editFaqId.value ? await api.updateFaq(editFaqId.value, ff) : await api.createFaq(ff)
    message.success('Saved'); showFaqForm.value = false; loadFaqs()
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

async function delFaq(id: number) {
  try { await api.deleteFaq(id); loadFaqs() } catch (e) { message.error(errMsg(e)) }
}

// ── CMS Pages ─────────────────────────────────────────────────────────────────
const cmsPages    = ref<any[]>([])
const showCmsEdit = ref(false)
const cmsTarget   = ref<any>(null)
const cmsForm     = reactive({ title:'', content:'' })

const loadCms     = async () => { try { cmsPages.value = (await api.cmsPages()).data } catch {} }

function openCmsEdit(p: any) {
  cmsTarget.value = p
  Object.assign(cmsForm, { title: p.title, content: p.content || '' })
  showCmsEdit.value = true
}

async function saveCms() {
  if (!cmsTarget.value) return
  saving.value = true
  try {
    await api.updateCmsPage(cmsTarget.value.page_type, cmsTarget.value.language_code, cmsForm)
    message.success('Saved'); showCmsEdit.value = false; loadCms()
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

// ── Email Templates ───────────────────────────────────────────────────────────
const emailTemplates    = ref<any[]>([])
const showTemplateEdit  = ref(false)
const tmplTarget        = ref<any>(null)
const tmplForm          = reactive({ subject:'', body:'' })

const loadTemplates     = async () => { try { emailTemplates.value = (await api.emailTemplates()).data } catch {} }

function openTemplateEdit(t: any) {
  tmplTarget.value = t
  Object.assign(tmplForm, { subject: t.subject, body: t.body })
  showTemplateEdit.value = true
}

async function saveTemplate() {
  if (!tmplTarget.value) return
  saving.value = true
  try {
    await api.updateTemplate(tmplTarget.value.type, tmplTarget.value.language_code, tmplForm)
    message.success('Saved'); showTemplateEdit.value = false
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

onMounted(() => { loadPosts(); loadFaqs(); loadCms(); loadTemplates() })
</script>
<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }
</style>
