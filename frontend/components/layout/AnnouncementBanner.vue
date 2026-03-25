<template>
  <div
    v-if="current"
    class="bg-emerald-600 text-white text-xs sm:text-sm text-center py-2 px-4 font-medium relative"
  >
    <span>{{ current.title }}</span>
    <span v-if="current.subtitle" class="hidden sm:inline ml-1 opacity-80">
      — {{ current.subtitle }}
    </span>
    <NuxtLink
      v-if="current.link_url"
      :to="current.link_url"
      class="ml-2 underline underline-offset-2 hover:no-underline"
    >
      Shop now →
    </NuxtLink>
    <button
      class="absolute right-3 top-1/2 -translate-y-1/2 opacity-70 hover:opacity-100"
      @click="dismiss"
    >
      <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ banners: any[] }>()

const dismissed = ref<number[]>([])
const current   = computed(() =>
  props.banners.find(b => !dismissed.value.includes(b.id))
)

function dismiss() {
  if (current.value) dismissed.value.push(current.value.id)
}
</script>
