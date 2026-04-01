<template>
  <div v-if="post" class="container-store py-12 max-w-3xl mx-auto">
    <NuxtLink to="/blog" class="text-sm text-emerald-600 hover:underline flex items-center gap-1 mb-8">
      <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
      Back to Blog
    </NuxtLink>

    <div class="mb-6">
      <p class="text-xs text-emerald-600 font-semibold uppercase tracking-widest mb-3">
        {{ post.category?.name || 'Article' }}
      </p>
      <h1 class="font-head text-4xl font-bold text-zinc-900 mb-4">{{ post.title }}</h1>
      <div class="flex items-center gap-3 text-sm text-zinc-400">
        <span>{{ post.author || 'Editorial' }}</span>
        <span>·</span>
        <span>{{ formatDate(post.published_at) }}</span>
      </div>
    </div>

    <div v-if="post.cover_image_url" class="aspect-video rounded-3xl overflow-hidden mb-10">
      <img :src="post.cover_image_url" :alt="post.title" class="w-full h-full object-cover" />
    </div>

    <div class="prose max-w-none" v-html="post.content" />
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
const route = useRoute()
const api   = useApi()

const { data: post, error } = await useAsyncData(
  `blog-${route.params.slug}`,
  () => api.getBlog(route.params.slug as string) as Promise<any>
)
if (error.value) throw createError({ statusCode: 404 })

useHead({
  title:       `${post.value?.title} — OPPLII`,
  meta: [{ name: 'description', content: post.value?.seo_description || post.value?.excerpt || '' }],
})

function formatDate(d: string) { return d ? dayjs(d).format('MMMM D, YYYY') : '' }
</script>
