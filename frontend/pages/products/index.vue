<template>
  <div class="container-store py-10">
    <div class="flex flex-col lg:flex-row gap-8">

      <!-- ── Sidebar filters ────────────────────────────────────────── -->
      <aside class="lg:w-56 flex-shrink-0 space-y-6">
        <h1 class="font-head text-2xl font-bold text-zinc-900">{{ $t('nav.products') }}</h1>

        <!-- Search (mobile) -->
        <UInput
          v-model="search"
          :placeholder="$t('common.search')"
          icon="i-heroicons-magnifying-glass"
          class="lg:hidden"
          @input="debouncedSearch"
        />

        <!-- Category filter -->
        <div>
          <h3 class="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-3">Category</h3>
          <ul class="space-y-1">
            <li>
              <button
                class="w-full text-left text-sm px-3 py-2 rounded-xl transition-colors"
                :class="!selectedCategory ? 'bg-emerald-50 text-emerald-700 font-medium' : 'text-zinc-600 hover:bg-zinc-50'"
                @click="selectedCategory = null"
              >
                {{ $t('common.all') }}
              </button>
            </li>
            <li v-for="cat in categories" :key="cat.id">
              <button
                class="w-full text-left text-sm px-3 py-2 rounded-xl transition-colors"
                :class="selectedCategory === cat.id ? 'bg-emerald-50 text-emerald-700 font-medium' : 'text-zinc-600 hover:bg-zinc-50'"
                @click="selectedCategory = cat.id"
              >
                {{ cat.name }}
              </button>
            </li>
          </ul>
        </div>

        <!-- Price sort -->
        <div>
          <h3 class="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-3">Sort By</h3>
          <USelect v-model="sort" :options="sortOptions" size="sm" />
        </div>
      </aside>

      <!-- ── Product grid ────────────────────────────────────────────── -->
      <div class="flex-1">
        <!-- Desktop search + results bar -->
        <div class="hidden lg:flex items-center justify-between mb-6 gap-4">
          <UInput
            v-model="search"
            :placeholder="$t('common.search')"
            icon="i-heroicons-magnifying-glass"
            class="w-72"
            @input="debouncedSearch"
          />
          <p class="text-sm text-zinc-400 flex-shrink-0">
            {{ total }} {{ total === 1 ? 'product' : 'products' }}
          </p>
        </div>

        <!-- Loading skeleton -->
        <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-5">
          <div v-for="i in 8" :key="i" class="rounded-2xl bg-zinc-100 animate-pulse aspect-[3/4]" />
        </div>

        <!-- Products -->
        <div v-else-if="products.length" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-5">
          <ProductCard
            v-for="p in products"
            :key="p.id"
            :product="p"
            :wishlist-ids="wishlistIds"
          />
        </div>

        <!-- Empty -->
        <div v-else class="text-center py-20">
          <div class="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <UIcon name="i-heroicons-face-frown" class="w-8 h-8 text-zinc-300" />
          </div>
          <p class="font-head font-semibold text-zinc-600">No products found</p>
          <p class="text-sm text-zinc-400 mt-1">Try a different search or category</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center mt-10">
          <UPagination
            v-model="page"
            :total="total"
            :page-count="limit"
            :ui="{ wrapper: 'gap-1' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()
const auth  = useAuthStore()
const api   = useApi()
const route = useRoute()
const router= useRouter()

useHead({ title: `Products — MyStore` })

// State
const search          = ref((route.query.q as string) || '')
const selectedCategory= ref<number | null>(null)
const sort            = ref('rating_desc')
const page            = ref(1)
const limit           = 20

// Sort options
const sortOptions = [
  { value: 'rating_desc',  label: 'Top Rated' },
  { value: 'created_desc', label: 'Newest' },
  { value: 'name_asc',     label: 'Name A-Z' },
]

// Categories
const { data: categoriesData } = await useAsyncData('categories', () =>
  api.getCategories() as Promise<any[]>
)
const categories = computed(() => categoriesData.value ?? [])

// Products
const { data: productsData, pending: loading, refresh } = await useAsyncData(
  'products',
  () => api.listProducts({
    page:        page.value,
    limit,
    search:      search.value || undefined,
    category_id: selectedCategory.value || undefined,
    sort:        sort.value,
  }) as Promise<any>,
  { watch: [page, sort, selectedCategory] }
)

const products   = computed(() => productsData.value?.items ?? [])
const total      = computed(() => productsData.value?.total ?? 0)
const totalPages = computed(() => productsData.value?.pages ?? 1)

// Debounced search
const debouncedSearch = useDebounceFn(() => {
  page.value = 1
  refresh()
}, 400)

// Wishlist ids
const { data: wishlistIds } = await useAsyncData(
  'wishlist-ids-listing',
  () => auth.isLoggedIn ? api.getWishlistIds() as Promise<number[]> : Promise.resolve([]),
  { default: () => [] as number[] }
)
</script>
