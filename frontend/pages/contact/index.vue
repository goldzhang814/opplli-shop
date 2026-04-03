<template>
  <div class="container-store py-12 max-w-3xl mx-auto">
    <div class="text-center mb-12">
      <h1 class="font-head text-4xl font-bold text-zinc-900 mb-3">{{ $t('nav.contact') }}</h1>
      <p class="text-zinc-500">Have a question? We're here to help.</p>
    </div>

    <div class="grid sm:grid-cols-2 gap-8">
      <!-- Contact methods -->
      <div class="space-y-4">
        <h2 class="font-head font-semibold text-zinc-900 mb-2">Get in touch</h2>

        <a
          v-for="c in contactLinks"
          :key="c.label"
          :href="c.href"
          target="_blank"
          rel="noopener"
          class="flex items-center gap-4 p-4 bg-zinc-50 hover:bg-emerald-50 rounded-2xl transition-colors group"
        >
          <div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:bg-emerald-500 transition-colors">
            <UIcon :name="c.icon" class="w-5 h-5 text-zinc-500 group-hover:text-white transition-colors" />
          </div>
          <div>
            <p class="font-medium text-zinc-900 text-sm">{{ c.label }}</p>
            <p class="text-xs text-zinc-500">{{ c.value }}</p>
          </div>
          <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4 text-zinc-300 ml-auto" />
        </a>
      </div>

      <!-- FAQ shortcut -->
      <div class="bg-emerald-50 rounded-2xl p-6 flex flex-col justify-between">
        <div>
          <div class="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center mb-4">
            <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5 text-white" />
          </div>
          <h3 class="font-head font-semibold text-zinc-900 mb-2">Check our FAQ first</h3>
          <p class="text-sm text-zinc-600 leading-relaxed">
            Most questions are answered in our FAQ section. Browse by category to find quick answers.
          </p>
        </div>
        <UButton to="/faq" variant="solid" class="mt-5">
          Browse FAQ →
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({ title: 'Contact — OPPLII' })

// Contact methods loaded from site_settings via API
const api = useApi()
const { data: settings } = await useAsyncData('contact-settings', async () => {
  try {
    // Fetch individual settings
    const keys = ['contact_whatsapp', 'contact_facebook', 'contact_telegram', 'contact_email']
    const results: Record<string, string> = {}
    // Settings returned as array from /admin — for public we hardcode defaults
    return results
  } catch { return {} }
}, { default: () => ({}) })

const contactLinks = computed(() => {
  const s = settings.value || {}
  const links = []
  if (s.contact_email || true) links.push({
    label: 'Email Support',
    value: (s as any).contact_email || 'service@opplii.com',
    href:  `mailto:${(s as any).contact_email || 'service@opplii.com'}`,
    icon:  'i-heroicons-envelope',
  })
  if ((s as any).contact_whatsapp) links.push({
    label: 'WhatsApp',
    value: (s as any).contact_whatsapp,
    href:  `https://wa.me/${(s as any).contact_whatsapp.replace(/\D/g, '')}`,
    icon:  'i-lucide-message-circle',
  })
  if ((s as any).contact_facebook) links.push({
    label: 'Facebook',
    value: 'Message us on Facebook',
    href:  (s as any).contact_facebook,
    icon:  'i-lucide-facebook',
  })
  if ((s as any).contact_telegram) links.push({
    label: 'Telegram',
    value: (s as any).contact_telegram,
    href:  `https://t.me/${(s as any).contact_telegram}`,
    icon:  'i-lucide-send',
  })
  return links
})
</script>
