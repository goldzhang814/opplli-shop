<template>
  <div class="flex gap-3 py-3 border-b border-zinc-100 last:border-0 animate-fade-in">
    <!-- Image -->
    <NuxtLink :to="`/products/${item.product_slug}`" @click="useCartStore().closeCart()">
      <div class="w-18 h-18 rounded-xl bg-zinc-100 overflow-hidden flex-shrink-0">
        <img
          v-if="item.cover_image"
          :src="item.cover_image"
          :alt="item.product_name"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-2xl">🌿</div>
      </div>
    </NuxtLink>

    <!-- Info -->
    <div class="flex-1 min-w-0">
      <NuxtLink
        :to="`/products/${item.product_slug}`"
        class="font-medium text-sm text-zinc-900 hover:text-emerald-600 transition-colors line-clamp-2"
        @click="useCartStore().closeCart()"
      >
        {{ item.product_name }}
      </NuxtLink>

      <!-- Variant attrs -->
      <div v-if="item.variant_attrs" class="flex flex-wrap gap-1 mt-0.5">
        <span
          v-for="(val, key) in item.variant_attrs"
          :key="key"
          class="text-xs text-zinc-500 bg-zinc-100 px-1.5 py-0.5 rounded-md capitalize"
        >
          {{ key }}: {{ val }}
        </span>
      </div>

      <!-- Price + qty -->
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center gap-1.5">
          <span class="font-semibold text-sm">${{ item.subtotal.toFixed(2) }}</span>
          <span v-if="item.compare_price && item.compare_price > item.unit_price"
            class="text-xs text-zinc-400 line-through">
            ${{ (item.compare_price * item.quantity).toFixed(2) }}
          </span>
        </div>

        <!-- Qty controls -->
        <div class="flex items-center gap-1 bg-zinc-100 rounded-xl p-0.5">
          <button
            class="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-white text-zinc-600 transition-colors text-xs"
            :disabled="item.quantity <= 1 || updating"
            @click="updateQty(item.quantity - 1)"
          >
            −
          </button>
          <span class="w-6 text-center text-sm font-medium">{{ item.quantity }}</span>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-white text-zinc-600 transition-colors text-xs"
            :disabled="item.quantity >= item.stock || updating"
            @click="updateQty(item.quantity + 1)"
          >
            +
          </button>
        </div>
      </div>
    </div>

    <!-- Remove -->
    <button
      class="text-zinc-300 hover:text-red-400 transition-colors flex-shrink-0"
      :disabled="updating"
      @click="remove"
    >
      <UIcon name="i-heroicons-trash" class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  item: {
    sku_id:        number
    product_name:  string
    product_slug:  string
    variant_attrs: Record<string, string> | null
    quantity:      number
    unit_price:    number
    compare_price: number | null
    subtotal:      number
    stock:         number
    cover_image:   string | null
  }
}>()

const emit    = defineEmits<{ updated: []; removed: [] }>()
const api     = useApi()
const updating= ref(false)

async function updateQty(qty: number) {
  updating.value = true
  try {
    await api.updateCartItem(props.item.sku_id, qty)
    emit('updated')
  } catch { /* silent */ }
  finally { updating.value = false }
}

async function remove() {
  updating.value = true
  try {
    await api.removeCartItem(props.item.sku_id)
    emit('removed')
  } catch { /* silent */ }
  finally { updating.value = false }
}
</script>
