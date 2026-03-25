<template>
  <div v-if="page" class="container-store py-12 max-w-3xl mx-auto">
    <h1 class="font-head text-4xl font-bold text-zinc-900 mb-8">{{ page.title }}</h1>
    <div class="prose max-w-none" v-html="page.content" />
  </div>
  <div v-else class="container-store py-20 text-center">
    <p class="text-zinc-400">Page not found.</p>
    <UButton to="/" class="mt-4">Go Home</UButton>
  </div>
</template>

<script setup lang="ts">
const route  = useRoute()
const { locale } = useI18n()
const api    = useApi()

// Convert URL slug back to page_type (about-us → about_us)
const pageType = computed(() => (route.params.type as string).replace(/-/g, '_'))

const { data: page } = await useAsyncData(
  `cms-${pageType.value}`,
  () => api.getCmsPage(pageType.value, locale.value).catch(() => null) as Promise<any>
)

useHead({ title: `${page.value?.title || 'Page'} — MyStore` })
</script>
