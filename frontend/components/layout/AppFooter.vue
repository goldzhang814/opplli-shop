<template>
  <footer class="bg-zinc-900 text-zinc-400 mt-auto">
    <div class="container-store py-14">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
        <!-- Brand -->
        <div class="md:col-span-1">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-xl bg-emerald-500 flex items-center justify-center">
              <span class="text-white font-bold text-sm font-head">O</span>
            </div>
            <span class="font-head font-semibold text-white text-base">OPPLII</span>
          </div>
          <p class="text-sm leading-relaxed mb-5">
            <!-- Premium, clinically formulated skin care products for your everyday needs.-->
            Premium, carefully designed products for your daily living needs.
          </p>
          <!-- Social links -->
          <div class="flex gap-3">
            <a
              v-for="s in socials"
              :key="s.href"
              :href="s.href"
              target="_blank"
              rel="noopener"
              class="w-9 h-9 rounded-xl bg-zinc-800 hover:bg-emerald-600 flex items-center justify-center transition-colors"
            >
              <UIcon :name="s.icon" class="w-4 h-4 text-zinc-400 group-hover:text-white" />
            </a>
          </div>
        </div>

        <!-- Shop -->
        <div>
          <h4 class="font-head font-semibold text-white text-sm uppercase tracking-widest mb-4">
            {{ $t('footer.links.shop') }}
          </h4>
          <ul class="space-y-2.5">
            <li v-for="link in shopLinks" :key="link.to">
              <NuxtLink :to="link.to" class="text-sm hover:text-emerald-400 transition-colors">
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Help -->
        <div>
          <h4 class="font-head font-semibold text-white text-sm uppercase tracking-widest mb-4">
            {{ $t('footer.links.help') }}
          </h4>
          <ul class="space-y-2.5">
            <li v-for="link in helpLinks" :key="link.to">
              <NuxtLink :to="link.to" class="text-sm hover:text-emerald-400 transition-colors">
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div>
          <h4 class="font-head font-semibold text-white text-sm uppercase tracking-widest mb-2">
            {{ $t('footer.newsletter') }}
          </h4>
          <p class="text-sm mb-4">{{ $t('footer.newsletterSub') }}</p>
          <form class="flex gap-2" @submit.prevent="submitNewsletter">
            <UInput
              v-model="email"
              type="email"
              :placeholder="$t('footer.emailPlaceholder')"
              required
              class="flex-1"
              size="sm"
              :disabled="subscribed"
            />
            <UButton
              type="submit"
              size="sm"
              :loading="subLoading"
              :disabled="subscribed"
            >
              {{ subscribed ? '✓' : $t('footer.subscribe') }}
            </UButton>
          </form>
          <p v-if="subscribed" class="text-xs text-emerald-400 mt-2">
            {{ $t('footer.subscribed') }}
          </p>
        </div>
      </div>

      <div class="border-t border-zinc-800 mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p class="text-xs">© {{ new Date().getFullYear() }} Hong Kong Global Cross-border Trading Co., Limited. All rights reserved.</p>
        <div class="flex flex-wrap gap-x-5 gap-y-1 justify-center">
          <NuxtLink
            v-for="link in legalLinks"
            :key="link.to"
            :to="link.to"
            class="text-xs hover:text-emerald-400 transition-colors"
          >
            {{ link.label }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { t } = useI18n()
const { locale } = useI18n()
const api   = useApi()

const email      = ref('')
const subscribed = ref(false)
const subLoading = ref(false)

async function submitNewsletter() {
  subLoading.value = true
  try {
    await api.subscribe({ email: email.value, source: 'footer', lang: locale.value })
    subscribed.value = true
  } catch { /* silent */ }
  finally { subLoading.value = false }
}

const socials = [
  { href: '#', icon: 'i-lucide-instagram' },
  { href: '#', icon: 'i-lucide-facebook' },
  { href: '#', icon: 'i-lucide-twitter' },
]

const shopLinks = computed(() => [
  { to: '/products',      label: t('nav.products') },
  { to: '/blog',          label: t('nav.blog') },
  { to: '/pages/about-us',label: t('nav.about') },
])

const helpLinks = computed(() => [
  { to: '/faq',                    label: t('nav.faq') },
  { to: '/contact',                label: t('nav.contact') },
  { to: '/pages/shipping-policy',  label: 'Shipping Policy' },
  { to: '/pages/return-policy',    label: 'Returns' },
])

const legalLinks = [
  { to: '/pages/privacy-policy',   label: 'Privacy Policy' },
  { to: '/pages/terms-of-service', label: 'Terms of Service' },
  { to: '/pages/cookie-policy',    label: 'Cookie Policy' },
  { to: '/pages/user-data-deletion',    label: 'User Data Deletion' },
]
</script>
