<template>
  <!-- Overlay -->
  <Transition name="fade">
    <div
      v-if="cart.isOpen"
      class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[60]"
      @click="cart.closeCart()"
    />
  </Transition>

  <!-- Drawer -->
  <Transition name="slide-right">
    <aside
      v-if="cart.isOpen"
      class="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white z-[61] flex flex-col shadow-2xl"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-zinc-100">
        <div class="flex items-center gap-2">
          <h2 class="font-head font-semibold text-lg">{{ $t('cart.title') }}</h2>
          <span
            v-if="cart.itemCount > 0"
            class="bg-emerald-100 text-emerald-700 text-xs font-semibold px-2 py-0.5 rounded-full"
          >
            {{ cart.itemCount }}
          </span>
        </div>
        <UButton icon="i-heroicons-x-mark" variant="ghost" color="gray" @click="cart.closeCart()" />
      </div>

      <!-- Free shipping bar -->
      <div v-if="!cart.isEmpty && threshold > 0" class="px-5 py-3 bg-emerald-50 border-b border-emerald-100">
        <div v-if="remaining <= 0" class="flex items-center gap-2 text-sm text-emerald-700 font-medium">
          <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
          You've unlocked free shipping! 🎉
        </div>
        <div v-else class="space-y-1.5">
          <p class="text-xs text-emerald-700">
            {{ $t('cart.spendMore', { amount: remaining.toFixed(2) }) }}
          </p>
          <div class="h-1.5 bg-emerald-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-emerald-500 rounded-full transition-all duration-500"
              :style="{ width: `${Math.min(100, (cart.subtotal / threshold) * 100)}%` }"
            />
          </div>
        </div>
      </div>

      <!-- Items -->
      <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        <template v-if="cart.isEmpty">
          <div class="flex flex-col items-center justify-center h-full text-center py-16">
            <div class="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mb-4">
              <UIcon name="i-heroicons-shopping-bag" class="w-8 h-8 text-zinc-300" />
            </div>
            <p class="font-head font-semibold text-zinc-700 mb-1">{{ $t('cart.empty') }}</p>
            <p class="text-sm text-zinc-400 mb-5">{{ $t('cart.emptyDesc') }}</p>
            <UButton @click="cart.closeCart(); navigateTo('/products')">
              {{ $t('cart.continueShopping') }}
            </UButton>
          </div>
        </template>

        <CartItem
          v-for="item in cart.items"
          :key="item.sku_id"
          :item="item"
          @updated="refreshCart"
          @removed="refreshCart"
        />
      </div>

      <!-- Footer -->
      <div v-if="!cart.isEmpty" class="border-t border-zinc-100 px-5 py-4 space-y-3">
        <div class="flex justify-between items-center">
          <span class="text-zinc-600">{{ $t('cart.subtotal') }}</span>
          <span class="font-head font-semibold text-lg">${{ cart.subtotal.toFixed(2) }}</span>
        </div>
        <UButton
          size="lg"
          block
          @click="cart.closeCart(); navigateTo('/checkout')"
        >
          {{ $t('cart.checkout') }} · ${{ cart.subtotal.toFixed(2) }}
        </UButton>
        <UButton
          variant="ghost"
          color="gray"
          size="sm"
          block
          @click="cart.closeCart()"
        >
          {{ $t('cart.continueShopping') }}
        </UButton>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
const cart      = useCartStore()
const api       = useApi()
const auth      = useAuthStore()

const threshold = ref(50)   // default; loaded from shipping estimate

const remaining = computed(() =>
  Math.max(0, threshold.value - cart.subtotal)
)

async function refreshCart() {
  try {
    const data = await api.getCart() as any
    cart.setCart(data)
  } catch { /* silent */ }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active        { transition: opacity 0.25s ease; }
.fade-enter-from,
.fade-leave-to            { opacity: 0; }

.slide-right-enter-active,
.slide-right-leave-active { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.slide-right-enter-from,
.slide-right-leave-to     { transform: translateX(100%); }
</style>
