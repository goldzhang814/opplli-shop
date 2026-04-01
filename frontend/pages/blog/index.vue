<template>
  <div class="container-store py-10">
    <div class="text-center mb-12">
      <h1 class="font-head text-4xl font-bold text-zinc-900 mb-3">Blog</h1>
      <p class="text-zinc-500 max-w-lg mx-auto">Tips, guides, and insights for healthy skin.</p>
    </div>

    <!-- Category filter -->
    <div class="flex flex-wrap gap-2 justify-center mb-10">
      <button
        class="px-4 py-2 rounded-full text-sm font-medium transition-colors"
        :class="!selectedCategory ? 'bg-emerald-500 text-white' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'"
        @click="selectedCategory = null"
      >
        All
      </button>
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="px-4 py-2 rounded-full text-sm font-medium transition-colors"
        :class="selectedCategory === cat.id ? 'bg-emerald-500 text-white' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'"
        @click="selectedCategory = cat.id"
      >
        {{ cat.name }}
      </button>
    </div>

    <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="rounded-2xl bg-zinc-100 animate-pulse h-72" />
    </div>

    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink
        v-for="post in posts"
        :key="post.id"
        :to="`/blog/${post.slug}`"
        class="group bg-white rounded-2xl border border-zinc-100 overflow-hidden hover:shadow-lg transition-all"
      >
        <div class="aspect-video bg-zinc-100 overflow-hidden">
          <img
            v-if="post.cover_image_url"
            :src="post.cover_image_url"
            :alt="post.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-4xl">📝</div>
        </div>
        <div class="p-5">
          <p class="text-xs text-emerald-600 font-semibold uppercase tracking-widest mb-2">
            {{ post.category?.name || 'Article' }}
          </p>
          <h2 class="font-head font-bold text-zinc-900 line-clamp-2 group-hover:text-emerald-700 transition-colors mb-2">
            {{ post.title }}
          </h2>
          <p v-if="post.excerpt" class="text-sm text-zinc-500 line-clamp-2 mb-3">{{ post.excerpt }}</p>
          <div class="flex items-center justify-between text-xs text-zinc-400">
            <span>{{ post.author || 'Editorial' }}</span>
            <span>{{ formatDate(post.published_at) }}</span>
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
useHead({ title: 'Blog — OPPLII' })

const api              = useApi()
const selectedCategory = ref<number | null>(null)

const { data: categoriesData } = await useAsyncData('blog-cats', () => api.getBlogCategories() as Promise<any[]>)
const categories = computed(() => categoriesData.value ?? [])

const { data: postsData, pending: loading } = await useAsyncData(
  'blog-posts',
  () => api.listBlog({ category_id: selectedCategory.value || undefined }) as Promise<any>,
  { watch: [selectedCategory] }
)
const posts = computed(() => postsData.value?.items ?? [])

function formatDate(d: string) { return d ? dayjs(d).format('MMM D, YYYY') : '' }
</script>
