<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <n-button quaternary @click="$router.back()">
        <template #icon><n-icon :component="ArrowBackOutline"/></template>
      </n-button>
      <h2 class="page-title">{{ isEdit ? 'Edit Product' : 'New Product' }}</h2>
    </div>

    <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
      <!-- ── Left ── -->
      <n-gi span="3 l:2">

        <!-- Basic Info -->
        <n-card title="Product Info" :bordered="false" style="border-radius:14px;margin-bottom:16px">
          <n-form :model="form" label-placement="top" size="medium">
            <n-form-item label="Product Name *">
              <n-input v-model:value="form.name" placeholder="e.g. Salicylic Acid Treatment" @input="autoSlug"/>
            </n-form-item>
            <n-grid :cols="2" :x-gap="12">
              <n-gi>
                <n-form-item label="Slug">
                  <n-input v-model:value="form.slug" placeholder="auto-generated" style="font-family:monospace;font-size:13px"/>
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="Category">
                  <n-tree-select
                    v-model:value="form.category_id"
                    :options="categoryTreeOptions"
                    clearable placeholder="Select category"
                    key-field="value" label-field="label" children-field="children"
                    :render-prefix="renderCategoryPrefix"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>
            <n-form-item label="Short Description">
              <n-input v-model:value="form.short_desc" type="textarea" :rows="2"/>
            </n-form-item>
            <n-form-item label="Full Description">
              <n-input v-model:value="form.description" type="textarea" :rows="8" placeholder="HTML content or plain text"/>
            </n-form-item>
          </n-form>
        </n-card>

        <!-- Images -->
        <n-card title="Product Images" :bordered="false" style="border-radius:14px;margin-bottom:16px">
          <div v-if="images.length" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px">
            <div v-for="img in images" :key="img.id"
              style="position:relative;width:100px;height:100px;border-radius:10px;overflow:hidden;border:1px solid #e5e7eb">
              <img :src="img.url" style="width:100%;height:100%;object-fit:cover"/>
              <div v-if="img.sort_order===0"
                style="position:absolute;top:4px;left:4px;background:#10b981;color:#fff;font-size:9px;font-weight:700;padding:2px 5px;border-radius:4px">
                COVER
              </div>
              <button class="img-del-btn" @click="deleteImage(img.id)">✕</button>
            </div>
          </div>
          <div class="upload-area" :class="{dragover:isDragOver}"
            @click="triggerUpload" @dragover.prevent="isDragOver=true"
            @dragleave="isDragOver=false" @drop.prevent="onDrop">
            <div v-if="uploading" style="display:flex;flex-direction:column;align-items:center;gap:8px">
              <n-spin size="medium"/>
              <span style="font-size:13px;color:#6b7280">Uploading {{ uploadProgress }}%…</span>
            </div>
            <div v-else style="display:flex;flex-direction:column;align-items:center;gap:8px">
              <div style="font-size:28px">🖼️</div>
              <p style="font-size:13px;font-weight:500;color:#374151">Click or drag images here</p>
              <p style="font-size:11px;color:#9ca3af">JPG, PNG, WebP — max 10MB each</p>
              <n-button size="small" style="margin-top:4px">Browse Files</n-button>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" multiple style="display:none" @change="onFileChange"/>
          <p v-if="!isEdit" style="font-size:12px;color:#f59e0b;margin-top:8px">
            💡 Save the product first, then upload images.
          </p>
        </n-card>

        <!-- SEO -->
        <n-card title="SEO" :bordered="false" style="border-radius:14px;margin-bottom:16px">
          <n-form :model="form" label-placement="top" size="medium">
            <n-form-item label="SEO Title">
              <n-input v-model:value="form.seo_title" placeholder="Override default title"/>
            </n-form-item>
            <n-form-item label="SEO Description">
              <n-input v-model:value="form.seo_description" type="textarea" :rows="2"/>
            </n-form-item>
          </n-form>
        </n-card>

        <!-- ── SKU / Variants ── -->
        <n-card title="SKUs / Variants" :bordered="false" style="border-radius:14px">

          <!-- Step 1: Variant axes -->
          <div style="margin-bottom:16px">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
              <div>
                <span style="font-weight:600;font-size:14px;color:#18181b">Step 1 — Define Variant Axes</span>
                <span style="font-size:12px;color:#9ca3af;margin-left:8px">e.g. Color, Size, Material…</span>
              </div>
              <n-button size="small" dashed @click="addAxis">
                <template #icon><n-icon :component="AddOutline"/></template>
                Add Axis
              </n-button>
            </div>

            <div v-if="axes.length === 0"
              style="padding:20px;text-align:center;background:#f9fafb;border-radius:10px;border:1px dashed #e5e7eb">
              <p style="font-size:13px;color:#9ca3af">
                No variant axes — product has a single SKU (no variants).
              </p>
            </div>

            <div v-for="(axis, ai) in axes" :key="ai"
              style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;background:#f9fafb;border-radius:10px;padding:12px">
              <!-- Axis name -->
              <div style="flex-shrink:0;width:130px">
                <p style="font-size:11px;color:#6b7280;margin-bottom:4px;font-weight:500">AXIS NAME</p>
                <n-input
                  v-model:value="axis.name"
                  size="small"
                  placeholder="Color"
                  @change="onAxisChange"
                />
              </div>
              <!-- Values as tags -->
              <div style="flex:1">
                <p style="font-size:11px;color:#6b7280;margin-bottom:4px;font-weight:500">
                  VALUES <span style="color:#9ca3af;font-weight:400">(press Enter or comma to add)</span>
                </p>
                <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;min-height:32px;background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:4px 8px">
                  <n-tag
                    v-for="(val, vi) in axis.values"
                    :key="vi"
                    size="small"
                    closable
                    type="info"
                    @close="removeValue(ai, vi)"
                    style="cursor:default"
                  >
                    {{ val }}
                  </n-tag>
                  <input
                    class="tag-input"
                    :placeholder="axis.values.length ? '' : 'Red, Blue, Black…'"
                    @keydown="onValueKeydown($event, ai)"
                    @blur="onValueBlur($event, ai)"
                  />
                </div>
              </div>
              <!-- Remove axis -->
              <n-button size="small" quaternary type="error" style="margin-top:18px;flex-shrink:0" @click="removeAxis(ai)">
                <template #icon><n-icon :component="TrashOutline"/></template>
              </n-button>
            </div>
          </div>

          <!-- Generate button -->
          <div v-if="axes.length > 0" style="display:flex;align-items:center;gap:12px;margin-bottom:20px;padding:12px 16px;background:#f0fdf4;border-radius:10px;border:1px solid #bbf7d0">
            <div style="flex:1">
              <p style="font-size:13px;font-weight:500;color:#065f46">
                Step 2 — Generate SKUs
              </p>
              <p style="font-size:12px;color:#059669;margin-top:2px">
                Will create <strong>{{ cartesianCount }}</strong> SKU{{ cartesianCount !== 1 ? 's' : '' }} from
                {{ axes.map(a => `${a.values.length} ${a.name || 'values'}`).join(' × ') }}
              </p>
            </div>
            <n-button type="primary" size="medium" @click="generateSkus" :disabled="cartesianCount === 0">
              ⚡ Generate SKUs
            </n-button>
          </div>

          <!-- Step 3: SKU table -->
          <div v-if="skus.length > 0">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
              <span style="font-weight:600;font-size:14px;color:#18181b">
                {{ axes.length > 0 ? 'Step 3 — ' : '' }}SKU List
                <n-tag size="small" style="margin-left:6px">{{ skus.length }}</n-tag>
              </span>
              <!-- Batch actions -->
              <div v-if="skus.length > 1" style="display:flex;align-items:center;gap:8px">
                <span style="font-size:12px;color:#6b7280">Batch set:</span>
                <n-input-number
                  v-model:value="batchPrice"
                  placeholder="Price"
                  size="small"
                  :min="0"
                  :precision="2"
                  prefix="$"
                  style="width:110px"
                />
                <n-input-number
                  v-model:value="batchStock"
                  placeholder="Stock"
                  size="small"
                  :min="0"
                  style="width:90px"
                />
                <n-button size="small" @click="applyBatch">Apply All</n-button>
              </div>
            </div>

            <!-- SKU rows -->
            <div style="overflow-x:auto">
              <table class="sku-table">
                <thead>
                  <tr>
                    <th v-for="axis in axes" :key="axis.name">{{ axis.name || 'Variant' }}</th>
                    <th>SKU Code</th>
                    <th>Price ($) *</th>
                    <th>Compare ($)</th>
                    <th>Stock</th>
                    <th>Low Alert</th>
                    <th>Free Ship</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(sku, si) in skus" :key="si" :class="{inactive: !sku.is_active}">
                    <!-- Variant attr cells -->
                    <td v-for="axis in axes" :key="axis.name">
                      <span class="attr-badge">{{ sku.variant_attrs?.[axis.name] ?? '—' }}</span>
                    </td>
                    <!-- SKU fields -->
                    <td>
                      <n-input v-model:value="sku.sku_code" size="small" placeholder="AUTO"
                        style="min-width:110px;font-family:monospace;font-size:12px"/>
                    </td>
                    <td>
                      <n-input-number v-model:value="sku.price" size="small" :min="0.01"
                        :precision="2" style="min-width:90px"/>
                    </td>
                    <td>
                      <n-input-number v-model:value="sku.compare_price" size="small" :min="0"
                        :precision="2" style="min-width:90px" :placeholder="undefined"/>
                    </td>
                    <td>
                      <n-input-number v-model:value="sku.stock" size="small" :min="0"
                        style="min-width:80px"/>
                    </td>
                    <td>
                      <n-input-number v-model:value="sku.low_stock_threshold" size="small"
                        :min="0" style="min-width:80px"/>
                    </td>
                    <td style="text-align:center">
                      <n-switch v-model:value="sku.free_shipping" size="small"/>
                    </td>
                    <td>
                      <n-button size="tiny" quaternary type="error" @click="skus.splice(si,1)">
                        <template #icon><n-icon :component="TrashOutline"/></template>
                      </n-button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Add single SKU (when no axes) -->
            <n-button v-if="axes.length === 0" dashed block style="margin-top:12px" @click="addBlankSku">
              + Add SKU
            </n-button>
          </div>

          <!-- Empty state when no axes and no skus -->
          <div v-if="skus.length === 0 && axes.length === 0"
            style="padding:20px;text-align:center;background:#f9fafb;border-radius:10px;border:1px dashed #e5e7eb;margin-top:8px">
            <n-button dashed @click="addBlankSku">+ Add Single SKU</n-button>
          </div>
        </n-card>
      </n-gi>

      <!-- ── Right sidebar ── -->
      <n-gi span="3 l:1">
        <n-card title="Status" :bordered="false" style="border-radius:14px;margin-bottom:16px">
          <n-form-item label="Published">
            <n-switch v-model:value="form.is_published"/>
          </n-form-item>
          <n-space vertical>
            <n-button type="primary" block :loading="saving" @click="save">
              {{ isEdit ? 'Save Changes' : 'Create Product' }}
            </n-button>
            <n-button block @click="$router.back()">Cancel</n-button>
          </n-space>
        </n-card>

        <n-card v-if="isEdit" title="Images" :bordered="false" style="border-radius:14px">
          <p style="font-size:13px;color:#6b7280;margin-bottom:4px">
            {{ images.length }} image{{ images.length !== 1 ? 's' : '' }}
          </p>
          <p style="font-size:12px;color:#9ca3af">First image is the cover photo.</p>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBackOutline, AddOutline, TrashOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'

const route   = useRoute()
const router  = useRouter()
const message = useMessage()
const saving  = ref(false)

const isEdit    = computed(() => !!route.params.id)
const productId = computed(() => Number(route.params.id))

// ── Categories ────────────────────────────────────────────────────────────────
const categories = ref<any[]>([])
const categoryTreeOptions = computed(() => {
  const roots = categories.value.filter((c: any) => !c.parent_id && c.is_active !== false)
  return roots.map((parent: any) => {
    const children = categories.value.filter(
      (c: any) => c.parent_id === parent.id && c.is_active !== false
    )
    return {
      label: parent.name, value: parent.id,
      children: children.length ? children.map((c: any) => ({ label: c.name, value: c.id })) : undefined,
    }
  })
})
function renderCategoryPrefix({ option }: any) {
  return h('span', { style: 'margin-right:4px;font-size:12px' }, option.children?.length ? '📁' : '🏷️')
}

// ── Form ──────────────────────────────────────────────────────────────────────
const form = reactive({
  name: '', slug: '', short_desc: '', description: '',
  category_id: null as number | null, is_published: false,
  seo_title: '', seo_description: '',
})
function autoSlug() {
  if (!isEdit.value) {
    form.slug = form.name.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-')
  }
}

// ── Variant axes ──────────────────────────────────────────────────────────────
interface Axis { name: string; values: string[] }
const axes = ref<Axis[]>([])

function addAxis() {
  axes.value.push({ name: '', values: [] })
}
function removeAxis(i: number) {
  axes.value.splice(i, 1)
}
function removeValue(ai: number, vi: number) {
  axes.value[ai].values.splice(vi, 1)
}
function onAxisChange() { /* just triggers reactivity */ }

function onValueKeydown(e: KeyboardEvent, ai: number) {
  const input = e.target as HTMLInputElement
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addValueFromInput(input, ai)
  } else if (e.key === 'Backspace' && input.value === '' && axes.value[ai].values.length) {
    axes.value[ai].values.pop()
  }
}
function onValueBlur(e: FocusEvent, ai: number) {
  addValueFromInput(e.target as HTMLInputElement, ai)
}
function addValueFromInput(input: HTMLInputElement, ai: number) {
  const raw = input.value.replace(/,/g, '').trim()
  if (raw && !axes.value[ai].values.includes(raw)) {
    axes.value[ai].values.push(raw)
  }
  input.value = ''
}

// ── Cartesian product ─────────────────────────────────────────────────────────
const cartesianCount = computed(() => {
  const validAxes = axes.value.filter(a => a.name && a.values.length > 0)
  if (!validAxes.length) return 0
  return validAxes.reduce((acc, a) => acc * a.values.length, 1)
})

function cartesian(arrays: string[][]): string[][] {
  return arrays.reduce<string[][]>(
    (acc, arr) => acc.flatMap(combo => arr.map(val => [...combo, val])),
    [[]]
  )
}

function generateSkus() {
  const validAxes = axes.value.filter(a => a.name.trim() && a.values.length > 0)
  if (!validAxes.length) {
    message.warning('Add at least one axis with values first')
    return
  }

  const combos = cartesian(validAxes.map(a => a.values))

  // Preserve existing SKU data by matching variant_attrs
  const existingMap = new Map(
    skus.value.map(s => [JSON.stringify(s.variant_attrs), s])
  )

  skus.value = combos.map(combo => {
    const attrs: Record<string, string> = {}
    validAxes.forEach((axis, i) => { attrs[axis.name] = combo[i] })

    const key = JSON.stringify(attrs)
    const existing = existingMap.get(key)

    // Auto-generate SKU code from attr values
    const autoCode = combo.join('-').toUpperCase().replace(/\s+/g, '')

    return {
      id:       existing?.id || undefined,  // ← 加这一行
      sku_code: existing?.sku_code || autoCode,
      price:    existing?.price    || 0,
      compare_price:       existing?.compare_price       || null,
      stock:               existing?.stock               || 0,
      low_stock_threshold: existing?.low_stock_threshold || 5,
      free_shipping:       existing?.free_shipping       || false,
      is_active:           true,
      variant_attrs:       attrs,
    }
  })

  message.success(`Generated ${skus.value.length} SKUs`)
}

// ── SKUs ──────────────────────────────────────────────────────────────────────
interface Sku {
  id?: number
  sku_code: string
  price: number
  compare_price: number | null
  stock: number
  low_stock_threshold: number
  free_shipping: boolean
  is_active: boolean
  variant_attrs: Record<string, string> | null
}
const skus = ref<Sku[]>([])

function addBlankSku() {
  skus.value.push({
    sku_code: '', price: 0, compare_price: null,
    stock: 0, low_stock_threshold: 5, free_shipping: false,
    is_active: true, variant_attrs: null,
  })
}

// ── Batch set price/stock ─────────────────────────────────────────────────────
const batchPrice = ref<number | null>(null)
const batchStock = ref<number | null>(null)

function applyBatch() {
  skus.value.forEach(s => {
    if (batchPrice.value !== null) s.price = batchPrice.value
    if (batchStock.value !== null) s.stock = batchStock.value
  })
  message.success('Applied to all SKUs')
}

// ── Images ────────────────────────────────────────────────────────────────────
interface ProductImage { id: number; url: string; sort_order: number }
const images       = ref<ProductImage[]>([])
const uploading    = ref(false)
const uploadProgress = ref(0)
const isDragOver   = ref(false)
const fileInput    = ref<HTMLInputElement | null>(null)

function triggerUpload() {
  if (!isEdit.value) { message.warning('Save product first, then upload images.'); return }
  fileInput.value?.click()
}
async function uploadFiles(files: File[]) {
  if (!isEdit.value) { message.warning('Save product first.'); return }
  const imgs = files.filter(f => f.type.startsWith('image/'))
  if (!imgs.length) { message.error('Please select image files'); return }
  uploading.value = true; uploadProgress.value = 0
  let done = 0
  for (const file of imgs) {
    try {
      const fd = new FormData(); fd.append('file', file); fd.append('alt_text', file.name.replace(/\.[^.]+$/, ''))
      await api.uploadImage(productId.value, fd)
      done++; uploadProgress.value = Math.round((done / imgs.length) * 100)
    } catch (e) { message.error(`Failed: ${file.name}`) }
  }
  uploading.value = false
  message.success(`${done} image${done !== 1 ? 's' : ''} uploaded`)
  await loadImages()
}
async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  await uploadFiles(Array.from(input.files))
  input.value = ''
}
function onDrop(e: DragEvent) {
  isDragOver.value = false
  uploadFiles(Array.from(e.dataTransfer?.files || []))
}
async function deleteImage(imageId: number) {
  try { await api.deleteImage(productId.value, imageId); await loadImages(); message.success('Deleted') }
  catch (e) { message.error(errMsg(e)) }
}
async function loadImages() {
  if (!isEdit.value) return
  try {
    const { data } = await api.product(productId.value)
    images.value = (data.images || []).sort((a: any, b: any) => a.sort_order - b.sort_order)
  } catch { /* silent */ }
}

// ── Save ──────────────────────────────────────────────────────────────────────
async function save() {
  if (!form.name.trim()) { message.warning('Product name is required'); return }
  if (!skus.value.length) { message.warning('At least one SKU is required'); return }

  saving.value = true
  try {
    const skuData = skus.value.map(({ id, ...s }) => ({
      ...s,
      sku_code: s.sku_code || `${form.name.slice(0,8).toUpperCase().replace(/\s/g,'-')}-${Math.random().toString(36).slice(2,6).toUpperCase()}`,
    }))

    if (isEdit.value) {
      await api.updateProduct(productId.value, form)

    // 1. 当前界面上的 SKU id 集合（有 id 说明是已存在的）
    const currentIds = new Set(
      skus.value.filter((s: any) => s.id).map((s: any) => s.id)
    )

    // 2. 数据库里原有的 SKU id 集合
    const { data: existingProduct } = await api.product(productId.value)
    const dbIds = new Set((existingProduct.skus || []).map((s: any) => s.id))

    // 3. 数据库有、界面没有 → 删除
    for (const dbId of dbIds) {
      if (!currentIds.has(dbId)) {
        try {
          await api.deleteSku(productId.value, dbId)
        } catch (e: any) {
          message.error(`Update SKU failed: ${e?.response?.data?.detail || e.message}`)
          return // 直接退出 save()
        }
      }
    }

      // Sync SKUs: update existing, create new
      for (const sku of skuData) {
        const skuId = (sku as any).id
        if (skuId) {
          // 已有 SKU → update
          const { id, ...updatePayload } = sku as any
          await api.updateSku(productId.value, skuId, updatePayload).catch((e: any) => {
            message.error(`Update SKU failed: ${e?.response?.data?.detail || e.message}`)
          })
        } else {
          // 新 SKU → create
          await api.createSku(productId.value, sku).catch((e: any) => {
            message.error(`Create SKU failed: ${e?.response?.data?.detail || e.message}`)
          })
        }
      }
      message.success('Saved!')
    } else {
      const { data } = await api.createProduct({ ...form, skus: skuData })
      message.success('Product created! You can now upload images.')
      router.push(`/products/${data.id}/edit`)
    }
  } catch (e) { message.error(errMsg(e)) }
  finally { saving.value = false }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  categories.value = (await api.categories()).data
  if (isEdit.value) {
    const { data } = await api.product(productId.value)
    Object.assign(form, {
      name: data.name, slug: data.slug, short_desc: data.short_desc || '',
      description: data.description || '', category_id: data.category_id,
      is_published: data.is_published, seo_title: data.seo_title || '',
      seo_description: data.seo_description || '',
    })
    if (data.skus?.length) {
      skus.value = data.skus.map((s: any) => ({ ...s, variant_attrs: s.variant_attrs || null }))
      // Reconstruct axes from existing SKU attrs
      const attrKeys = new Set<string>()
      const attrValues: Record<string, Set<string>> = {}
      for (const sku of data.skus) {
        if (sku.variant_attrs) {
          for (const [k, v] of Object.entries(sku.variant_attrs)) {
            attrKeys.add(k)
            if (!attrValues[k]) attrValues[k] = new Set()
            attrValues[k].add(v as string)
          }
        }
      }
      if (attrKeys.size > 0) {
        axes.value = Array.from(attrKeys).map(k => ({
          name: k,
          values: Array.from(attrValues[k]),
        }))
      }
    }
    images.value = (data.images || []).sort((a: any, b: any) => a.sort_order - b.sort_order)
  }
})
</script>

<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }

.upload-area {
  border:2px dashed #e5e7eb; border-radius:12px; padding:28px 16px;
  text-align:center; cursor:pointer; transition:all 0.2s; background:#fafafa;
}
.upload-area:hover { border-color:#10b981; background:#f0fdf4; }
.upload-area.dragover { border-color:#10b981; background:#ecfdf5; transform:scale(1.01); }

.img-del-btn {
  position:absolute; top:4px; right:4px; width:20px; height:20px;
  border-radius:50%; background:rgba(0,0,0,0.55); border:none; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-size:11px;
}
.img-del-btn:hover { background:rgba(239,68,68,0.85); }

.tag-input {
  border:none; outline:none; background:transparent;
  font-size:13px; color:#374151; min-width:80px; flex:1; padding:2px 4px;
}

.sku-table { width:100%; border-collapse:collapse; font-size:13px; }
.sku-table th {
  text-align:left; padding:8px 10px; font-size:11px; font-weight:600;
  color:#6b7280; text-transform:uppercase; letter-spacing:0.04em;
  background:#f9fafb; border-bottom:1px solid #e5e7eb;
  white-space:nowrap;
}
.sku-table td { padding:6px 8px; border-bottom:1px solid #f3f4f6; vertical-align:middle; }
.sku-table tr:hover td { background:#f9fafb; }
.sku-table tr.inactive td { opacity:0.45; }

.attr-badge {
  display:inline-block; background:#e0f2fe; color:#0369a1;
  border-radius:6px; padding:2px 8px; font-size:12px; font-weight:500;
  white-space:nowrap;
}
</style>
