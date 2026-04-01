<template>
  <div>
    <!-- ── HERO ─────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-zinc-50 min-h-[90vh] flex items-center">
      <!-- bg dot pattern -->
      <div class="absolute inset-0 opacity-40"
        style="background-image:radial-gradient(circle, #d1fae5 1px, transparent 1px); background-size:32px 32px" />

      <div class="container-store relative z-10 py-20">
        <div class="grid lg:grid-cols-2 gap-16 items-center">
          <!-- Copy -->
          <div class="animate-fade-up">
            <div class="inline-flex items-center gap-2 bg-emerald-100 text-emerald-700 text-sm font-medium px-4 py-2 rounded-full mb-6">
              <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              Clinically Formulated
            </div>

            <h1 class="font-head text-5xl lg:text-6xl xl:text-7xl font-bold text-zinc-900 leading-[1.05] mb-6">
              {{ $t('home.heroTitle') }}
            </h1>

            <p class="text-lg text-zinc-500 leading-relaxed mb-8 max-w-lg">
              {{ $t('home.heroSub') }}
            </p>

            <div class="flex flex-col sm:flex-row gap-3 mb-10">
              <UButton size="xl" to="/products" class="group">
                {{ $t('home.shopNow') }}
                <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </UButton>
              <UButton size="xl" variant="outline" color="gray" to="/pages/about-us">
                {{ $t('home.howItWorks') }}
              </UButton>
            </div>

            <!-- Trust row -->
            <div class="flex flex-wrap gap-x-6 gap-y-3">
              <div v-for="t in trustItems" :key="t.label" class="flex items-center gap-2 text-sm text-zinc-500">
                <UIcon :name="t.icon" class="w-4 h-4 text-emerald-500" />
                {{ t.label }}
              </div>
            </div>
          </div>

          <!-- Hero visual -->
          <div class="animate-fade-in delay-200 relative">
            <div class="relative aspect-[4/5] max-w-md mx-auto">
              <div class="absolute inset-0 bg-gradient-to-br from-emerald-200 to-emerald-300 rounded-[3rem] rotate-3 opacity-60" />
              <div class="absolute inset-0 bg-gradient-to-br from-emerald-50 to-white rounded-[3rem] -rotate-1 shadow-2xl flex items-center justify-center">
                <span class="text-8xl">🌿</span>
              </div>

              <!-- Floating cards -->
              <div class="absolute -right-5 top-10 bg-white rounded-2xl shadow-xl px-4 py-3 animate-fade-in delay-300">
                <div class="flex gap-0.5 mb-1">
                  <UIcon v-for="i in 5" :key="i" name="i-heroicons-star-solid" class="w-3.5 h-3.5 text-amber-400" />
                </div>
                <p class="text-xs font-semibold text-zinc-800">4.9 · 2,400+ reviews</p>
              </div>

              <div class="absolute -left-5 bottom-16 bg-white rounded-2xl shadow-xl px-4 py-3 animate-fade-in delay-400">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-xl bg-emerald-100 flex items-center justify-center">
                    <UIcon name="i-heroicons-check-badge" class="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <p class="text-xs font-bold text-zinc-900">93% Success Rate</p>
                    <p class="text-xs text-zinc-400">within 14 days</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── TRUST BAR ───────────────────────────────────────────────── -->
    <section class="bg-zinc-900 py-4">
      <div class="container-store">
        <div class="flex flex-wrap justify-center gap-x-10 gap-y-2">
          <span v-for="t in trustBadges" :key="t" class="text-sm text-zinc-400 font-medium">{{ t }}</span>
        </div>
      </div>
    </section>

    <!-- ── FEATURED PRODUCTS ──────────────────────────────────────── -->
    <section class="py-20 bg-white">
      <div class="container-store">
        <div class="flex items-end justify-between mb-10">
          <div>
            <p class="text-sm text-emerald-600 font-semibold uppercase tracking-widest mb-2">Our Collection</p>
            <h2 class="font-head text-4xl font-bold text-zinc-900">{{ $t('home.featured') }}</h2>
          </div>
          <UButton variant="ghost" color="gray" to="/products" class="hidden sm:flex">
            {{ $t('home.viewAll') }} →
          </UButton>
        </div>

        <div v-if="productsLoading" class="grid grid-cols-2 lg:grid-cols-4 gap-5">
          <div v-for="i in 4" :key="i" class="rounded-2xl bg-zinc-100 animate-pulse aspect-[3/4]" />
        </div>

        <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-5">
          <ProductCard
            v-for="p in featuredProducts"
            :key="p.id"
            :product="p"
            :wishlist-ids="wishlistIds"
          />
        </div>

        <div class="text-center mt-8 sm:hidden">
          <UButton variant="outline" color="gray" to="/products">
            {{ $t('home.viewAll') }}
          </UButton>
        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS ───────────────────────────────────────────── -->
    <section class="py-20 bg-zinc-50">
      <div class="container-store">
        <div class="text-center mb-14">
          <h2 class="font-head text-4xl font-bold text-zinc-900 mb-4">Simple, effective routine</h2>
          <p class="text-zinc-500 max-w-lg mx-auto">Three steps to healthier skin — no dermatologist visit required.</p>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="(step, i) in steps"
            :key="i"
            class="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="w-12 h-12 bg-emerald-100 rounded-2xl flex items-center justify-center mb-5">
              <span class="text-2xl">{{ step.emoji }}</span>
            </div>
            <span class="text-xs font-bold tracking-widest text-emerald-400 uppercase">Step 0{{ i + 1 }}</span>
            <h3 class="font-head font-bold text-xl text-zinc-900 mt-2 mb-3">{{ step.title }}</h3>
            <p class="text-zinc-500 text-sm leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── NEWSLETTER ─────────────────────────────────────────────── -->
    <section class="py-20 bg-emerald-600">
      <div class="container-store text-center max-w-xl mx-auto">
        <h2 class="font-head text-3xl font-bold text-white mb-3">{{ $t('footer.newsletter') }}</h2>
        <p class="text-emerald-100 mb-8">{{ $t('footer.newsletterSub') }}</p>
        <form class="flex gap-3 max-w-md mx-auto" @submit.prevent="subscribe">
          <UInput
            v-model="newsEmail"
            type="email"
            :placeholder="$t('footer.emailPlaceholder')"
            required
            class="flex-1"
            size="lg"
            :disabled="subscribed"
          />
          <UButton type="submit" size="lg" color="white" variant="solid" :loading="subLoading">
            {{ subscribed ? '✓' : $t('footer.subscribe') }}
          </UButton>
        </form>
        <p v-if="subscribed" class="text-emerald-200 text-sm mt-3">{{ $t('footer.subscribed') }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const auth   = useAuthStore()
const api    = useApi()

useHead({ title: 'OPPLII — Premium Skin Care' })

// Products
const { data: productsData, pending: productsLoading } = await useAsyncData(
  'featured-products',
  () => api.listProducts({ limit: 8, sort: 'rating_desc' }) as Promise<any>
)
const featuredProducts = computed(() => productsData.value?.items ?? [])

// Wishlist ids (if logged in)
const { data: wishlistIds } = await useAsyncData(
  'wishlist-ids',
  () => auth.isLoggedIn ? api.getWishlistIds() as Promise<number[]> : Promise.resolve([]),
  { default: () => [] as number[] }
)

// Newsletter
const newsEmail  = ref('')
const subscribed = ref(false)
const subLoading = ref(false)

async function subscribe() {
  subLoading.value = true
  try {
    await api.subscribe({ email: newsEmail.value, source: 'homepage', lang: locale.value })
    subscribed.value = true
  } catch { /* silent */ }
  finally { subLoading.value = false }
}

const trustItems = computed(() => [
  { icon: 'i-heroicons-shield-check', label: t('home.trustBar.fda') },
  { icon: 'i-heroicons-truck',        label: t('home.trustBar.free') },
  { icon: 'i-heroicons-arrow-uturn-left', label: t('home.trustBar.money') },
  { icon: 'i-heroicons-star',         label: t('home.trustBar.rating') },
])

const trustBadges = [
  '🧪 Dermatologist Tested', '✅ FDA-Compliant', '🚚 Free US Shipping $50+',
  '💰 30-Day Return', '🌿 Clean Ingredients',
]

const steps = [
  { emoji: '🧼', title: 'Cleanse',      desc: 'Start with a clean, dry surface for maximum absorption.' },
  { emoji: '💧', title: 'Apply',        desc: 'Apply a thin, targeted layer directly to affected area.' },
  { emoji: '✨', title: 'See Results',  desc: 'Consistent use delivers visible improvement within 7–14 days.' },
]
</script>
