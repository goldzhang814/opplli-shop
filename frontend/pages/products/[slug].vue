<template>
  <div v-if="product" class="container-store py-10">
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm text-zinc-400 mb-8">
      <NuxtLink to="/" class="hover:text-emerald-600 transition-colors">Home</NuxtLink>
      <span>/</span>
      <NuxtLink to="/products" class="hover:text-emerald-600 transition-colors">Products</NuxtLink>
      <span>/</span>
      <span class="text-zinc-600 truncate max-w-48">{{ product.name }}</span>
    </nav>

    <div class="grid lg:grid-cols-2 gap-12 xl:gap-16">
      <!-- ── Images ────────────────────────────────────────────────── -->
      <div class="space-y-4">
        <div class="relative aspect-square rounded-3xl overflow-hidden bg-zinc-50 shadow-sm">
          <img
            v-if="activeImage"
            :src="activeImage.url"
            :alt="product.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-8xl">🌿</div>

          <!-- Wishlist -->
          <button
            v-if="auth.isLoggedIn"
            class="absolute top-4 right-4 w-10 h-10 bg-white rounded-2xl shadow-md flex items-center justify-center hover:scale-110 transition-transform"
            @click="toggleWishlist"
          >
            <UIcon
              :name="inWishlist ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'"
              class="w-5 h-5"
              :class="inWishlist ? 'text-red-500' : 'text-zinc-400'"
            />
          </button>
        </div>

        <!-- Thumbnails -->
        <div v-if="product.images?.length > 1" class="flex gap-3 overflow-x-auto pb-1">
          <button
            v-for="(img, i) in product.images"
            :key="i"
            class="flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden border-2 transition-all"
            :class="activeImageIdx === i ? 'border-emerald-500' : 'border-transparent'"
            @click="activeImageIdx = i"
          >
            <img :src="img.url" :alt="`${product.name} ${i + 1}`" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>

      <!-- ── Product info ───────────────────────────────────────────── -->
      <div>
        <p v-if="product.category_name" class="text-sm text-emerald-600 font-semibold uppercase tracking-widest mb-2">
          {{ product.category_name }}
        </p>

        <h1 class="font-head text-3xl xl:text-4xl font-bold text-zinc-900 leading-tight mb-4">
          {{ product.name }}
        </h1>

        <!-- Rating -->
        <div v-if="product.rating_count > 0" class="flex items-center gap-2 mb-5">
          <div class="flex gap-0.5">
            <UIcon
              v-for="i in 5"
              :key="i"
              name="i-heroicons-star-solid"
              class="w-4 h-4"
              :class="i <= Math.round(product.rating_avg) ? 'text-amber-400' : 'text-zinc-200'"
            />
          </div>
          <span class="text-sm font-semibold text-zinc-700">{{ product.rating_avg.toFixed(1) }}</span>
          <a href="#reviews" class="text-sm text-zinc-400 hover:text-emerald-600">
            ({{ product.rating_count }} {{ $t('product.reviews') }})
          </a>
        </div>

        <!-- Price -->
        <div class="flex items-baseline gap-3 mb-6">
          <span class="font-head text-3xl font-bold text-zinc-900">${{ selectedSku?.price.toFixed(2) }}</span>
          <span
            v-if="selectedSku?.compare_price && selectedSku.compare_price > selectedSku.price"
            class="text-lg text-zinc-400 line-through"
          >
            ${{ selectedSku.compare_price.toFixed(2) }}
          </span>
          <span
            v-if="salePercent > 0"
            class="bg-red-100 text-red-600 text-sm font-bold px-2 py-0.5 rounded-lg"
          >
            -{{ salePercent }}%
          </span>
        </div>

        <!-- Variant selectors -->
        <div v-for="attrKey in variantKeys" :key="attrKey" class="mb-5">
          <label class="text-sm font-semibold text-zinc-700 mb-2 block">
            {{ attrKey.charAt(0).toUpperCase() + attrKey.slice(1) }}:
            <span class="font-normal text-emerald-600">{{ selectedAttrs[attrKey] }}</span>
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="val in attrValues(attrKey)"
              :key="val"
              class="px-4 py-2 rounded-xl border text-sm font-medium transition-all"
              :class="selectedAttrs[attrKey] === val
                ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                : hasStock(attrKey, val)
                  ? 'border-zinc-200 text-zinc-700 hover:border-emerald-300'
                  : 'border-zinc-100 text-zinc-300 cursor-not-allowed line-through'"
              :disabled="!hasStock(attrKey, val)"
              @click="selectAttr(attrKey, val)"
            >
              {{ val }}
            </button>
          </div>
        </div>

        <!-- Stock indicator -->
        <div class="flex items-center gap-2 mb-6">
          <span
            class="w-2.5 h-2.5 rounded-full"
            :class="inStock ? 'bg-emerald-500' : 'bg-red-400'"
          />
          <span class="text-sm text-zinc-600">
            {{ inStock ? $t('product.inStock') : $t('product.outOfStock') }}
            <span v-if="inStock && selectedSku && selectedSku.stock <= 5" class="text-amber-600 ml-1">
              (Only {{ selectedSku.stock }} left!)
            </span>
          </span>
        </div>

        <!-- Qty + Add to cart -->
        <div class="flex gap-3 mb-6">
          <div class="flex items-center gap-1 bg-zinc-100 rounded-2xl p-1">
            <button
              class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-white transition-colors text-zinc-600 disabled:opacity-40"
              :disabled="qty <= 1"
              @click="qty--"
            >−</button>
            <span class="w-10 text-center font-semibold text-zinc-900">{{ qty }}</span>
            <button
              class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-white transition-colors text-zinc-600 disabled:opacity-40"
              :disabled="!inStock || qty >= (selectedSku?.stock ?? 0)"
              @click="qty++"
            >+</button>
          </div>

          <UButton
            size="xl"
            class="flex-1"
            :disabled="!inStock || addingToCart"
            :loading="addingToCart"
            @click="addToCart"
          >
            <UIcon name="i-heroicons-shopping-bag" class="w-5 h-5" />
            {{ inStock ? $t('product.addToCart') : $t('product.outOfStock') }}
          </UButton>
        </div>

        <!-- Trust row -->
        <div class="grid grid-cols-3 gap-3 py-5 border-y border-zinc-100">
          <div v-for="t in trustItems" :key="t.label" class="text-center">
            <UIcon :name="t.icon" class="w-5 h-5 text-emerald-500 mx-auto mb-1" />
            <p class="text-xs text-zinc-500">{{ t.label }}</p>
          </div>
        </div>

        <!-- Share -->
        <div class="flex items-center gap-3 mt-5">
          <span class="text-sm text-zinc-400">{{ $t('product.share') }}:</span>
          <button
            v-for="s in shareOptions"
            :key="s.label"
            class="text-zinc-400 hover:text-emerald-600 transition-colors text-sm"
            @click="share(s)"
          >
            {{ s.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Tabs (description / reviews) ──────────────────────────── -->
    <div class="mt-16">
      <div class="border-b border-zinc-200">
        <div class="flex gap-0">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="px-6 py-3.5 text-sm font-medium border-b-2 transition-colors -mb-px"
            :class="activeTab === tab.key
              ? 'border-emerald-500 text-emerald-700'
              : 'border-transparent text-zinc-500 hover:text-zinc-800'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="py-10 max-w-3xl">
        <!-- Description -->
        <div v-if="activeTab === 'description'">
          <div
            v-if="product.description"
            class="prose"
            v-html="product.description"
          />
          <p v-else class="text-zinc-400 italic">No description available.</p>
        </div>

        <!-- Reviews -->
        <div v-if="activeTab === 'reviews'" id="reviews">
          <!-- Rating summary -->
          <div v-if="product.rating_count > 0" class="flex items-center gap-6 mb-8 p-5 bg-zinc-50 rounded-2xl">
            <div class="text-center">
              <p class="font-head text-5xl font-bold text-zinc-900">{{ product.rating_avg.toFixed(1) }}</p>
              <div class="flex gap-0.5 justify-center mt-1">
                <UIcon
                  v-for="i in 5"
                  :key="i"
                  name="i-heroicons-star-solid"
                  class="w-4 h-4"
                  :class="i <= Math.round(product.rating_avg) ? 'text-amber-400' : 'text-zinc-200'"
                />
              </div>
              <p class="text-xs text-zinc-400 mt-1">{{ product.rating_count }} reviews</p>
            </div>
          </div>

          <!-- Review list -->
          <div v-if="reviewsLoading" class="space-y-4">
            <div v-for="i in 3" :key="i" class="h-24 bg-zinc-100 rounded-2xl animate-pulse" />
          </div>
          <div v-else-if="reviews.length" class="space-y-5">
            <div v-for="r in reviews" :key="r.id" class="border border-zinc-100 rounded-2xl p-5">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <div class="flex gap-0.5">
                    <UIcon
                      v-for="i in 5"
                      :key="i"
                      name="i-heroicons-star-solid"
                      class="w-3.5 h-3.5"
                      :class="i <= r.rating ? 'text-amber-400' : 'text-zinc-200'"
                    />
                  </div>
                  <p class="text-sm font-semibold text-zinc-800 mt-1">{{ r.reviewer_name || 'Anonymous' }}</p>
                </div>
                <div class="text-right">
                  <span v-if="r.is_verified_purchase" class="badge-verified text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-medium">
                    {{ $t('product.verifiedPurchase') }}
                  </span>
                  <p class="text-xs text-zinc-400 mt-1">{{ formatDate(r.created_at) }}</p>
                </div>
              </div>
              <p v-if="r.content" class="text-sm text-zinc-600 leading-relaxed">{{ r.content }}</p>
            </div>
          </div>
          <p v-else class="text-zinc-400">{{ $t('product.noReviews') }}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 404 -->
  <div v-else class="container-store py-20 text-center">
    <h2 class="font-head text-3xl font-bold text-zinc-700 mb-4">Product not found</h2>
    <UButton to="/products">Browse Products</UButton>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'

const route   = useRoute()
const { t }   = useI18n()
const auth    = useAuthStore()
const cart    = useCartStore()
const api     = useApi()
const toast   = useToast()

const slug = computed(() => route.params.slug as string)

// Product
const { data: product, error } = await useAsyncData(
  `product-${slug.value}`,
  () => api.getProduct(slug.value) as Promise<any>
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Product not found' })
}

useHead({
  title: `${product.value?.name} — MyStore`,
  meta: [
    { name: 'description', content: product.value?.seo_description || product.value?.short_desc || '' },
  ],
})

// Image
const activeImageIdx = ref(0)
const activeImage    = computed(() => product.value?.images?.[activeImageIdx.value])

// Variant selection
const variantKeys   = computed(() => {
  const skus = product.value?.skus ?? []
  if (!skus.length) return []
  return Object.keys(skus[0].variant_attrs ?? {})
})

const selectedAttrs = ref<Record<string, string>>({})
onMounted(() => {
  const firstSku = product.value?.skus?.[0]
  if (firstSku?.variant_attrs) {
    selectedAttrs.value = { ...firstSku.variant_attrs }
  }
})

const selectedSku = computed(() => {
  const skus = product.value?.skus ?? []
  return skus.find((s: any) =>
    variantKeys.value.every(k => s.variant_attrs?.[k] === selectedAttrs.value[k])
  ) ?? skus[0]
})

const inStock = computed(() => (selectedSku.value?.stock ?? 0) > 0)

const salePercent = computed(() => {
  const s = selectedSku.value
  if (!s?.compare_price || !s.price) return 0
  return Math.round((1 - s.price / s.compare_price) * 100)
})

function attrValues(key: string) {
  return [...new Set((product.value?.skus ?? []).map((s: any) => s.variant_attrs?.[key]))]
}

function hasStock(key: string, val: string) {
  const sku = (product.value?.skus ?? []).find((s: any) => s.variant_attrs?.[key] === val)
  return (sku?.stock ?? 0) > 0
}

function selectAttr(key: string, val: string) {
  selectedAttrs.value = { ...selectedAttrs.value, [key]: val }
}

// Wishlist
const inWishlist = ref(false)
onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      const ids = await api.getWishlistIds() as number[]
      inWishlist.value = ids.includes(product.value?.id)
    } catch { /* silent */ }
  }
})

async function toggleWishlist() {
  try {
    await api.toggleWishlist(product.value!.id)
    inWishlist.value = !inWishlist.value
  } catch { /* silent */ }
}

// Add to cart
const qty          = ref(1)
const addingToCart = ref(false)

async function addToCart() {
  if (!selectedSku.value) return
  addingToCart.value = true
  try {
    const data = await api.addToCart({ sku_id: selectedSku.value.id, quantity: qty.value }) as any
    cart.setCart(data)
    cart.openCart()
    toast.add({ title: t('product.addedToCart'), color: 'green', timeout: 2000 })
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally {
    addingToCart.value = false
  }
}

// Reviews
const activeTab = ref<'description' | 'reviews'>('description')

const { data: reviewsData, pending: reviewsLoading } = await useAsyncData(
  `reviews-${slug.value}`,
  () => api.listReviews(product.value?.id, { page: 1 }) as Promise<any>,
  { watch: [activeTab] }
)
const reviews = computed(() => reviewsData.value?.items ?? [])

// Tabs
const tabs = computed(() => [
  { key: 'description', label: t('product.description') },
  { key: 'reviews',     label: `${t('product.reviews')} (${product.value?.rating_count ?? 0})` },
])

// Trust items
const trustItems = [
  { icon: 'i-heroicons-shield-check',    label: 'FDA-Compliant' },
  { icon: 'i-heroicons-truck',           label: 'Free Ship $50+' },
  { icon: 'i-heroicons-arrow-uturn-left',label: '30-Day Return' },
]

// Share
const shareOptions = [
  { label: 'Copy Link', action: 'copy' },
  { label: 'Twitter',   action: 'twitter' },
]

function share(s: { label: string; action: string }) {
  const url = window.location.href
  if (s.action === 'copy') {
    navigator.clipboard.writeText(url)
    toast.add({ title: 'Link copied!', color: 'green', timeout: 2000 })
  } else if (s.action === 'twitter') {
    window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(product.value?.name ?? '')}`)
  }
}

function formatDate(d: string) {
  return dayjs(d).format('MMM D, YYYY')
}
</script>
