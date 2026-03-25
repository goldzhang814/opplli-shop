<template>
  <Transition name="slide-up">
    <div
      v-if="show"
      class="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:max-w-sm z-[80]"
    >
      <div class="bg-zinc-900 text-white rounded-2xl shadow-2xl p-5">
        <h4 class="font-head font-semibold text-sm mb-2">
          {{ config?.title || $t('cookie.title') }}
        </h4>
        <p class="text-xs text-zinc-400 leading-relaxed mb-4">
          {{ config?.description || $t('cookie.desc') }}
          <NuxtLink to="/pages/cookie-policy" class="underline hover:text-emerald-400 ml-1">
            Learn more
          </NuxtLink>
        </p>
        <div class="flex gap-2">
          <UButton size="sm" @click="accept">
            {{ config?.accept_btn || $t('cookie.accept') }}
          </UButton>
          <UButton size="sm" variant="outline" color="gray" @click="reject">
            {{ config?.reject_btn || $t('cookie.reject') }}
          </UButton>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const { locale }  = useI18n()
const consent     = useCookie('cookie_consent', { maxAge: 60 * 60 * 24 * 365 })
const show        = ref(false)
const config      = ref<any>(null)

onMounted(async () => {
  if (!consent.value) {
    show.value = true
    try {
      config.value = await useApi().getCookieConfig(locale.value)
    } catch { /* use default translations */ }
  }
})

function accept() {
  consent.value = 'accepted'
  show.value    = false
}

function reject() {
  consent.value = 'rejected'
  show.value    = false
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.slide-up-enter-from,
.slide-up-leave-to     { opacity: 0; transform: translateY(20px); }
</style>
