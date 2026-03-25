<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="text-center max-w-md">
      <div class="w-20 h-20 bg-zinc-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <span class="text-4xl">{{ error?.statusCode === 404 ? '🔍' : '⚡' }}</span>
      </div>
      <h1 class="font-head text-5xl font-bold text-zinc-900 mb-3">
        {{ error?.statusCode || 500 }}
      </h1>
      <p class="text-zinc-500 mb-8 leading-relaxed">
        {{ error?.statusCode === 404
          ? "The page you're looking for doesn't exist or has been moved."
          : error?.message || 'Something went wrong. Please try again.' }}
      </p>
      <div class="flex justify-center gap-3">
        <UButton @click="handleError">Go Home</UButton>
        <UButton variant="ghost" color="gray" @click="$router.back()">Go Back</UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ error: { statusCode: number; message: string } | null }>()

function handleError() {
  clearError({ redirect: '/' })
}
</script>
