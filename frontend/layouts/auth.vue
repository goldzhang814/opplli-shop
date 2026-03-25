<template>
  <div class="min-h-screen bg-zinc-50 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <NuxtLink to="/" class="inline-flex items-center gap-2 justify-center">
          <div class="w-10 h-10 rounded-2xl bg-emerald-500 flex items-center justify-center">
            <span class="text-white font-bold font-head">S</span>
          </div>
          <span class="font-head font-semibold text-xl text-zinc-900">MyStore</span>
        </NuxtLink>
      </div>
      <slot />
    </div>
  </div>
</template>
