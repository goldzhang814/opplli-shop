<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Categories</h2>
        <p class="page-sub">{{ categories.length }} categories</p>
      </div>
      <n-button type="primary" @click="openForm()">
        <template #icon><n-icon :component="AddOutline" /></template>
        New Category
      </n-button>
    </div>

    <n-card :bordered="false" style="border-radius:14px">
      <div v-if="loading" style="padding:40px;text-align:center"><n-spin /></div>
      <div v-else-if="!categories.length" style="padding:40px;text-align:center;color:#9ca3af">
        No categories yet
      </div>
      <n-data-table
        v-else
        :columns="columns"
        :data="categories"
        :bordered="false"
        size="small"
        :row-key="(r: any) => r.id"
      />
    </n-card>

    <!-- Form modal -->
    <n-modal v-model:show="showForm" :mask-closable="false">
      <n-card
        style="width:480px; border-radius:14px"
        :title="editId ? 'Edit Category' : 'New Category'"
      >
        <n-form :model="form" label-placement="top" size="medium">
          <n-form-item label="Name *">
            <n-input
              v-model:value="form.name"
              placeholder="e.g. Wart Treatment"
              @input="autoSlug"
            />
          </n-form-item>

          <n-form-item label="Slug">
            <n-input
              v-model:value="form.slug"
              placeholder="auto-generated from name"
              style="font-family:monospace; font-size:13px"
            />
            <template #feedback>Used in URLs, e.g. /products?category=wart-treatment</template>
          </n-form-item>

          <n-form-item label="Description">
            <n-input
              v-model:value="form.description"
              type="textarea"
              :rows="2"
              placeholder="Optional short description"
            />
          </n-form-item>

          <n-form-item label="Parent Category">
            <n-select
              v-model:value="form.parent_id"
              :options="parentOptions"
              placeholder="Top-level (no parent)"
              clearable
            />
          </n-form-item>

          <n-grid :cols="2" :x-gap="12">
            <n-gi>
              <n-form-item label="Sort Order">
                <n-input-number
                  v-model:value="form.sort_order"
                  :min="0"
                  style="width:100%"
                />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="Active">
                <n-switch v-model:value="form.is_active" />
              </n-form-item>
            </n-gi>
          </n-grid>
        </n-form>

        <n-space justify="end" style="margin-top:16px">
          <n-button @click="showForm = false">Cancel</n-button>
          <n-button type="primary" :loading="saving" @click="save">
            {{ editId ? 'Save Changes' : 'Create' }}
          </n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Delete confirm -->
    <n-modal v-model:show="showDelete">
      <n-card style="width:380px; border-radius:14px" title="Delete Category">
        <p style="color:#6b7280; margin-bottom:20px">
          Are you sure? Products in this category will be uncategorized.
        </p>
        <n-space justify="end">
          <n-button @click="showDelete = false">Cancel</n-button>
          <n-button type="error" :loading="deleting" @click="confirmDelete">Delete</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import { NTag, NButton, NIcon, NSpace, useMessage } from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'

const message    = useMessage()
const categories = ref<any[]>([])
const loading    = ref(false)
const saving     = ref(false)
const deleting   = ref(false)
const showForm   = ref(false)
const showDelete = ref(false)
const editId     = ref<number | null>(null)
const deleteId   = ref<number | null>(null)

const form = reactive({
  name:        '',
  slug:        '',
  description: '',
  parent_id:   null as number | null,
  sort_order:  0,
  is_active:   true,
})

// Parent options: only top-level categories (no parent)
const parentOptions = computed(() =>
  categories.value
    .filter(c => !c.parent_id && c.id !== editId.value)
    .map(c => ({ label: c.name, value: c.id }))
)

// Auto-generate slug from name
function autoSlug() {
  if (!editId.value) {
    form.slug = form.name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.categories()
    categories.value = data
  } catch (e) {
    message.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

function openForm(cat?: any) {
  editId.value = cat?.id ?? null
  Object.assign(form, cat
    ? {
        name:        cat.name,
        slug:        cat.slug,
        description: cat.description || '',
        parent_id:   cat.parent_id,
        sort_order:  cat.sort_order ?? 0,
        is_active:   cat.is_active,
      }
    : { name: '', slug: '', description: '', parent_id: null, sort_order: 0, is_active: true }
  )
  showForm.value = true
}

async function save() {
  if (!form.name.trim()) {
    message.warning('Name is required')
    return
  }
  saving.value = true
  try {
    const payload = {
      name:        form.name,
      slug:        form.slug || undefined,
      description: form.description || undefined,
      parent_id:   form.parent_id,
      sort_order:  form.sort_order,
      is_active:   form.is_active,
    }
    editId.value
      ? await api.updateCategory(editId.value, payload)
      : await api.createCategory(payload)

    message.success(editId.value ? 'Category updated' : 'Category created')
    showForm.value = false
    await load()
  } catch (e) {
    message.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

function promptDelete(id: number) {
  deleteId.value  = id
  showDelete.value= true
}

async function confirmDelete() {
  if (!deleteId.value) return
  deleting.value = true
  try {
    await api.updateCategory(deleteId.value, { is_active: false })
    message.success('Category deactivated')
    showDelete.value = false
    await load()
  } catch (e) {
    message.error(errMsg(e))
  } finally {
    deleting.value = false
  }
}

const columns = [
  {
    title: 'Name',
    key:   'name',
    render: (r: any) => {
      const indent = r.parent_id ? '    ' : ''
      return h('div', { style: 'display:flex; align-items:center; gap:8px' }, [
        r.parent_id
          ? h('span', { style: 'color:#d1d5db; font-size:16px' }, '↳')
          : null,
        h('span', { style: 'font-weight:500; font-size:13px' }, r.name),
      ])
    },
  },
  {
    title: 'Slug',
    key:   'slug',
    render: (r: any) => h(
      'code',
      { style: 'font-size:11px; background:#f3f4f6; padding:2px 6px; border-radius:4px; color:#6b7280' },
      r.slug
    ),
  },
  {
    title: 'Parent',
    key:   'parent_id',
    width: 140,
    render: (r: any) => {
      if (!r.parent_id) return h('span', { style: 'color:#9ca3af; font-size:12px' }, '—')
      const parent = categories.value.find(c => c.id === r.parent_id)
      return h('span', { style: 'font-size:12px' }, parent?.name || `#${r.parent_id}`)
    },
  },
  {
    title: 'Sort',
    key:   'sort_order',
    width: 70,
    render: (r: any) => h('span', { style: 'color:#9ca3af; font-size:12px' }, r.sort_order ?? 0),
  },
  {
    title: 'Status',
    key:   'is_active',
    width: 90,
    render: (r: any) => h(
      NTag,
      { type: r.is_active ? 'success' : 'default', size: 'small', round: true },
      () => r.is_active ? 'Active' : 'Hidden'
    ),
  },
  {
    title:  'Actions',
    key:    '_actions',
    width:  90,
    render: (r: any) => h(NSpace, { size: 'small' }, () => [
      h(
        NButton,
        { size: 'tiny', quaternary: true, onClick: () => openForm(r) },
        { default: () => h(NIcon, { component: CreateOutline }) }
      ),
      h(
        NButton,
        { size: 'tiny', quaternary: true, type: 'error', onClick: () => promptDelete(r.id) },
        { default: () => h(NIcon, { component: TrashOutline }) }
      ),
    ]),
  },
]

onMounted(load)
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
.page-sub    { font-size:13px; color:#9ca3af; margin-top:2px; }
</style>
