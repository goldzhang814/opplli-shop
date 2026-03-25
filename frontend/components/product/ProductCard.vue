<template>
  <NuxtLink
    :to="`/products/${product.slug}`"
    class="group bg-white rounded-2xl border border-zinc-100 hover:border-emerald-200 hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col"
  >
    <!-- Image -->
    <div class="relative aspect-square bg-zinc-50 overflow-hidden">
      <img
        v-if="product.cover_image"
        :src="product.cover_image"
        :alt="product.name"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-5xl">🌿</div>

      <!-- Wishlist btn -->
      <button
        v-if="auth.isLoggedIn"
        class="absolute top-3 right-3 w-8 h-8 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-sm hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
        @click.prevent="toggleWishlist"
      >
        <UIcon
          :name="inWishlist ? 'i-heroicons-heart-solid' : 'i-heroicons-heart'"
          class="w-4 h-4 transition-colors"
          :class="inWishlist ? 'text-red-500' : 'text-zinc-400'"
        />
      </button>

      <!-- Sale badge -->
      <div
        v-if="salePercent > 0"
        class="absolute top-3 left-3 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-lg"
      >
        -{{ salePercent }}%
      </div>
    </div>

    <!-- Info -->
    <div class="p-4 flex flex-col flex-1">
      <p v-if="product.category_name" class="text-xs text-emerald-600 font-medium uppercase tracking-wide mb-1">
        {{ product.category_name }}
      </p>
      <h3 class="font-head font-semibold text-zinc-900 text-sm leading-snug mb-2 line-clamp-2 group-hover:text-emerald-700 transition-colors">
        {{ product.name }}
      </h3>

      <!-- Rating -->
      <div v-if="product.rating_count > 0" class="flex items-center gap-1.5 mb-3">
        <div class="flex gap-0.5">
          <UIcon
            v-for="i in 5"
            :key="i"
            name="i-heroicons-star-solid"
            class="w-3 h-3"
            :class="i <= Math.round(product.rating_avg) ? 'text-amber-400' : 'text-zinc-200'"
          />
        </div>
        <span class="text-xs text-zinc-400">({{ product.rating_count }})</span>
      </div>
      <div v-else class="mb-3" />

      <!-- Price -->
      <div class="flex items-center justify-between mt-auto">
        <div class="flex items-baseline gap-1.5">
          <span class="font-head font-bold text-zinc-900">
            ${{ (product.min_price ?? 0).toFixed(2) }}
          </span>
          <span
            v-if="product.max_price && product.max_price > product.min_price"
            class="text-xs text-zinc-400"
          >
            – ${{ product.max_price.toFixed(2) }}
          </span>
        </div>

        <!-- Quick add -->
        <button
          class="w-8 h-8 bg-emerald-50 hover:bg-emerald-500 text-emerald-600 hover:text-white rounded-xl flex items-center justify-center transition-all duration-200 opacity-0 group-hover:opacity-100"
          @click.prevent="quickAdd"
        >
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
const props = defineProps<{
  product: {
    id:            number
    name:          string
    slug:          string
    category_name: string | null
    min_price:     number | null
    max_price:     number | null
    rating_avg:    number
    rating_count:  number
    cover_image:   string | null
    skus?:         Array<{ id: number; price: number; compare_price?: number }>
  }
  wishlistIds?: number[]
}>()

const auth   = useAuthStore()
const cart   = useCartStore()
const api    = useApi()
const toast  = useToast()
const { t }  = useI18n()

const inWishlist = computed(() =>
  props.wishlistIds?.includes(props.product.id) ?? false
)

const salePercent = computed(() => {
  const sku = props.product.skus?.[0]
  if (!sku?.compare_price || !sku.price) return 0
  return Math.round((1 - sku.price / sku.compare_price) * 100)
})

async function quickAdd() {
  const sku = props.product.skus?.[0]
  if (!sku) {
    navigateTo(`/products/${props.product.slug}`)
    return
  }
  try {
    const data = await api.addToCart({ sku_id: sku.id, quantity: 1 }) as any
    cart.setCart(data)
    cart.openCart()
    toast.add({ title: t('product.addedToCart'), color: 'green', timeout: 2000 })
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  }
}

async function toggleWishlist() {
  try {
    await api.toggleWishlist(props.product.id)
  } catch { /* silent */ }
}
</script>
