<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Products</h2>
        <p class="page-sub">{{ total }} products</p>
      </div>
      <n-button type="primary" @click="$router.push('/products/new')">
        <template #icon><n-icon :component="AddOutline" /></template>
        Add Product
      </n-button>
    </div>

    <n-card :bordered="false" style="border-radius:14px; margin-bottom:16px">
      <div style="display:flex; gap:12px; align-items:center">
        <n-input v-model:value="search" placeholder="Search products…" clearable style="width:260px"
          @update:value="debouncedLoad">
          <template #prefix><n-icon :component="SearchOutline" /></template>
        </n-input>
        <n-tree-select
          v-model:value="categoryFilter"
          :options="categoryTreeOptions"
          placeholder="All categories"
          clearable
          style="width:200px"
          key-field="value"
          label-field="label"
          children-field="children"
          @update:value="load"
        />
        <n-button @click="load" :loading="loading">
          <template #icon><n-icon :component="RefreshOutline" /></template>
        </n-button>
      </div>
    </n-card>

    <n-card :bordered="false" style="border-radius:14px">
      <n-data-table
        :columns="columns"
        :data="products"
        :loading="loading"
        :bordered="false"
        size="small"
        :row-key="(r: any) => r.id"
      />
      <div style="display:flex; justify-content:flex-end; margin-top:16px">
        <n-pagination v-model:page="page" :item-count="total" :page-size="20" @update:page="load" />
      </div>
    </n-card>

    <!-- Confirm delete -->
    <n-modal v-model:show="showDeleteConfirm">
      <n-card style="width:400px; border-radius:14px" title="Delete Product">
        <p style="color:#6b7280; margin-bottom:20px">Are you sure? This cannot be undone.</p>
        <n-space justify="end">
          <n-button @click="showDeleteConfirm = false">Cancel</n-button>
          <n-button type="error" :loading="deleting" @click="confirmDelete">Delete</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NTag, NButton, NIcon, NSpace, NImage, useMessage } from 'naive-ui'
import { SearchOutline, RefreshOutline, AddOutline, CreateOutline, TrashOutline, EyeOutline, EyeOffOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'
import { useDebounceFn } from '@vueuse/core'

const router  = useRouter()
const message = useMessage()

const products       = ref<any[]>([])
const total          = ref(0)
const page           = ref(1)
const loading        = ref(false)
const search         = ref('')
const categoryFilter = ref<number | null>(null)
const categories     = ref<any[]>([])
const showDeleteConfirm = ref(false)
const deleteTarget      = ref<number | null>(null)
const deleting          = ref(false)

const categoryTreeOptions = computed(() => {
  const roots = categories.value.filter((c: any) => !c.parent_id)
  return roots.map((parent: any) => {
    const children = categories.value.filter((c: any) => c.parent_id === parent.id)
    return {
      label: parent.name,
      value: parent.id,
      children: children.length
        ? children.map((c: any) => ({ label: c.name, value: c.id }))
        : undefined,
    }
  })
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.products({
      page: page.value, search: search.value || undefined,
      category_id: categoryFilter.value || undefined,
    })
    products.value = data.items
    total.value    = data.total
  } catch { /* silent */ }
  finally { loading.value = false }
}

const debouncedLoad = useDebounceFn(load, 400)

onMounted(async () => {
  const { data } = await api.categories()
  categories.value = data
  load()
})

async function togglePublish(p: any) {
  try {
    p.is_published ? await api.unpublishProduct(p.id) : await api.publishProduct(p.id)
    message.success(p.is_published ? 'Unpublished' : 'Published')
    load()
  } catch (e) { message.error(errMsg(e)) }
}

function promptDelete(id: number) {
  deleteTarget.value      = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.deleteProduct(deleteTarget.value)
    message.success('Deleted')
    showDeleteConfirm.value = false
    load()
  } catch (e) { message.error(errMsg(e)) }
  finally { deleting.value = false }
}

const columns = [
  {
    title: 'Product',
    key:   'name',
    render: (r: any) => h('div', { style: 'display:flex; align-items:center; gap:10px' }, [
      h('div', {
        style: 'width:40px; height:40px; border-radius:8px; background:#f3f4f6; overflow:hidden; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:18px'
      }, r.cover_image ? h('img', { src: r.cover_image, style: 'width:100%; height:100%; object-fit:cover' }) : '🌿'),
      h('div', {}, [
        h('p', { style: 'font-weight:500; font-size:13px; color:#18181b' }, r.name),
        h('p', { style: 'font-size:11px; color:#9ca3af; font-family:monospace' }, r.slug),
      ]),
    ]),
  },
  { title: 'Category', key: 'category_name', render: (r: any) => r.category_name || '—', width: 120 },
  {
    title: 'Price',
    key:   'min_price',
    render: (r: any) => {
      if (!r.min_price) return '—'
      const s = r.min_price === r.max_price ? `$${r.min_price.toFixed(2)}` : `$${r.min_price.toFixed(2)} – $${r.max_price.toFixed(2)}`
      return h('span', { style: 'font-weight:600' }, s)
    },
    width: 130,
  },
  {
    title: 'Rating',
    key:   'rating_avg',
    render: (r: any) => r.rating_count > 0 ? h('span', {}, `★ ${r.rating_avg.toFixed(1)} (${r.rating_count})`) : '—',
    width: 120,
  },
  {
    title: 'Status',
    key:   'is_published',
    render: (r: any) => h(NTag, { type: r.is_published ? 'success' : 'default', size: 'small', round: true },
      () => r.is_published ? 'Published' : 'Draft'),
    width: 100,
  },
  {
    title: 'Actions',
    key:   '_actions',
    width: 120,
    render: (r: any) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { size: 'tiny', quaternary: true, onClick: () => router.push(`/products/${r.id}/edit`) },
        { default: () => h(NIcon, { component: CreateOutline }) }),
      h(NButton, {
        size: 'tiny', quaternary: true,
        title: r.is_published ? 'Unpublish' : 'Publish',
        onClick: () => togglePublish(r),
      }, { default: () => h(NIcon, { component: r.is_published ? EyeOffOutline : EyeOutline }) }),
      h(NButton, { size: 'tiny', quaternary: true, type: 'error', onClick: () => promptDelete(r.id) },
        { default: () => h(NIcon, { component: TrashOutline }) }),
    ]),
  },
]
</script>

<style scoped>
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.page-title  { font-size:20px; font-weight:600; color:#18181b; }
.page-sub    { font-size:13px; color:#9ca3af; margin-top:2px; }
</style>
