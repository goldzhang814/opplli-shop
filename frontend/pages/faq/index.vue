<template>
  <div class="container-store py-12 max-w-3xl mx-auto">
    <div class="text-center mb-10">
      <h1 class="font-head text-4xl font-bold text-zinc-900">{{ $t('nav.faq') }}</h1>
    </div>

    <!-- Category tabs -->
    <div v-if="faqCategories.length" class="flex flex-wrap gap-2 mb-8">
      <button
        class="px-4 py-2 rounded-full text-sm font-medium transition-colors"
        :class="!selectedCat ? 'bg-emerald-500 text-white' : 'bg-zinc-100 text-zinc-600'"
        @click="selectedCat = null"
      >
        All
      </button>
      <button
        v-for="cat in faqCategories"
        :key="cat"
        class="px-4 py-2 rounded-full text-sm font-medium transition-colors"
        :class="selectedCat === cat ? 'bg-emerald-500 text-white' : 'bg-zinc-100 text-zinc-600'"
        @click="selectedCat = cat"
      >
        {{ cat }}
      </button>
    </div>

    <div class="space-y-3">
      <UAccordion
        :items="faqItems"
        :ui="{ item: { base: 'border border-zinc-100 rounded-2xl overflow-hidden' } }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const api        = useApi()
const selectedCat= ref<string | null>(null)

useHead({ title: 'FAQ — OPPLII' })

const { data: categoriesData } = await useAsyncData('faq-cats',
  () => api.getFaqCategories({ lang: locale.value }) as Promise<string[]>
)
const faqCategories = computed(() => categoriesData.value ?? [])

const { data: faqData } = await useAsyncData(
  'faq-list',
  () => api.getFaq({ lang: locale.value, category: selectedCat.value || undefined }) as Promise<any[]>,
  { watch: [selectedCat, locale] }
)

const faqItems = computed(() =>
  (faqData.value ?? []).map(f => ({
    label:   f.question,
    content: f.answer,
  }))
)
</script>
