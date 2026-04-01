<template>
  <div class="container-store py-10">
    <h1 class="font-head text-3xl font-bold text-zinc-900 mb-8">{{ $t('nav.wishlist') }}</h1>

    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-5">
      <div v-for="i in 4" :key="i" class="rounded-2xl bg-zinc-100 animate-pulse aspect-[3/4]" />
    </div>

    <div v-else-if="!items.length" class="text-center py-16">
      <div class="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-heart" class="w-8 h-8 text-zinc-300" />
      </div>
      <p class="font-head font-semibold text-zinc-600 mb-4">No saved items yet</p>
      <UButton to="/products">Browse Products</UButton>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
      <div v-for="item in items" :key="item.product_id" class="group relative">
        <NuxtLink :to="`/products/${item.slug}`" class="block bg-white rounded-2xl border border-zinc-100 overflow-hidden hover:shadow-lg transition-all">
          <div class="aspect-square bg-zinc-50">
            <img v-if="item.cover_image" :src="item.cover_image" :alt="item.product_name" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-4xl">🌿</div>
          </div>
          <div class="p-4">
            <p class="font-medium text-zinc-900 text-sm line-clamp-2">{{ item.product_name }}</p>
            <p v-if="item.min_price" class="font-head font-bold text-zinc-900 mt-1">${{ item.min_price.toFixed(2) }}</p>
          </div>
        </NuxtLink>

        <!-- Remove button -->
        <button
          class="absolute top-3 right-3 w-8 h-8 bg-white rounded-full shadow flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50"
          @click="removeFromWishlist(item.product_id)"
        >
          <UIcon name="i-heroicons-heart-solid" class="w-4 h-4 text-red-500" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: 'Wishlist — OPPLII' })

const api   = useApi()
const toast = useToast()

const { data: items, pending: loading, refresh } = await useAsyncData(
  'wishlist',
  () => api.getWishlist() as Promise<any[]>,
  { default: () => [] }
)

async function removeFromWishlist(productId: number) {
  try {
    await api.toggleWishlist(productId)
    await refresh()
  } catch { toast.add({ title: 'Failed to remove', color: 'red' }) }
}
</script>
