<template>
  <div class="container-store py-12 max-w-3xl mx-auto">
    <div class="text-center mb-12">
      <h1 class="font-head text-4xl font-bold text-zinc-900 mb-3">{{ $t('nav.contact') }}</h1>
      <p class="text-zinc-500">Have a question? We're here to help.</p>
    </div>

<div class="grid lg:grid-cols-[1.2fr_1fr] gap-8">
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

        <div class="border border-zinc-200 rounded-2xl p-5 bg-white shadow-sm">
          <p class="text-xs text-zinc-500 uppercase tracking-widest mb-3">Business Info</p>
          <p class="font-semibold text-zinc-900 text-sm">{{ businessInfo.name }}</p>
          <p class="text-xs text-zinc-500 mb-3">Reg. No. {{ businessInfo.registration }}</p>
          <p class="text-sm text-zinc-600">
            <strong>Address:</strong><br />
            {{ businessInfo.address }}
          </p>
          <p class="text-sm text-zinc-600 mt-2">
            <strong>Phone:</strong> {{ businessInfo.phone }}
          </p>
          <p class="text-sm text-zinc-600">
            <strong>Email:</strong> <a :href="`mailto:${businessInfo.email}`" class="text-emerald-600 hover:underline">{{ businessInfo.email }}</a>
          </p>
        </div>
      </div>

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
          Browse FAQ?
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
    return await api.getSiteSettings()
  } catch {
    return {}
  }
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
    icon:  'i-lucide-send',
  })
  return links
})

const businessInfo = computed(() => {
  const s = settings.value || {}
  return {
    name: s.company_name || 'Hong Kong Global Cross-border Trading Co., Limited',
    registration: s.business_registration_number || 'le_797UXoxZN1WoMSmJlXI2Yw',
    address: s.business_address || 'ROOM A16, FLAT 1, 7/F, BLOCK 3 NAN FUNG INDUSTRIAL CITY, 18 TIN HAU ROAD, TUEN MUN, N.T., HONG KONG',
    email: s.contact_email || 'service@opplii.com',
    phone: s.contact_phone || '+86 13632836027',
  }
})
</script>
