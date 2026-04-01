<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="scrolled ? 'bg-white/95 backdrop-blur-md shadow-sm' : 'bg-white'"
    style="height: var(--header-h)"
  >
    <!-- Announcement banner -->
    <AnnouncementBanner v-if="banners.length" :banners="banners" />

    <div class="container-store h-full flex items-center gap-4">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 flex-shrink-0">
        <div class="w-8 h-8 rounded-xl bg-emerald-500 flex items-center justify-center">
          <span class="text-white font-bold text-sm font-head">O</span>
        </div>
        <span class="font-head font-semibold text-lg text-zinc-900 hidden sm:block">
          {{ siteName }}
        </span>
      </NuxtLink>

      <!-- Desktop nav -->
      <nav class="hidden md:flex items-center gap-6 flex-1 justify-center">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="text-sm font-medium text-zinc-600 hover:text-emerald-600 transition-colors relative group"
          active-class="text-emerald-600"
        >
          {{ link.label }}
          <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-emerald-500 group-hover:w-full transition-all duration-200" />
        </NuxtLink>
      </nav>

      <!-- Right actions -->
      <div class="flex items-center gap-2 ml-auto">
        <!-- Search -->
        <UButton icon="i-heroicons-magnifying-glass" variant="ghost" color="gray"
          class="hidden sm:flex" @click="searchOpen = true" />

        <!-- Language picker -->
        <USelectMenu
          v-model="currentLocale"
          :options="localeOptions"
          value-attribute="code"
          option-attribute="name"
          class="hidden sm:flex w-24"
          size="xs"
        />

        <!-- Wishlist -->
        <NuxtLink v-if="auth.isLoggedIn" to="/wishlist">
          <UButton icon="i-heroicons-heart" variant="ghost" color="gray" />
        </NuxtLink>

        <!-- Account -->
        <UDropdown v-if="auth.isLoggedIn" :items="accountMenuItems">
          <UButton variant="ghost" color="gray" class="gap-2">
            <UAvatar
              :alt="auth.displayName"
              size="xs"
              :src="auth.user?.avatar_url ?? undefined"
            />
            <span class="hidden sm:inline text-sm">{{ auth.displayName }}</span>
            <UIcon name="i-heroicons-chevron-down" class="w-3 h-3" />
          </UButton>
        </UDropdown>
        <NuxtLink v-else to="/auth/login">
          <UButton variant="ghost" color="gray" size="sm">
            {{ $t('nav.signIn') }}
          </UButton>
        </NuxtLink>

        <!-- Cart -->
        <UButton
          variant="ghost"
          color="gray"
          class="relative"
          @click="cart.openCart()"
        >
          <UIcon name="i-heroicons-shopping-bag" class="w-5 h-5" />
          <span
            v-if="cart.itemCount > 0"
            class="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-emerald-500 text-white text-xs rounded-full flex items-center justify-center font-semibold px-1"
          >
            {{ cart.itemCount }}
          </span>
        </UButton>

        <!-- Mobile menu -->
        <UButton
          icon="i-heroicons-bars-3"
          variant="ghost"
          color="gray"
          class="md:hidden"
          @click="mobileOpen = !mobileOpen"
        />
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <div
        v-if="mobileOpen"
        class="md:hidden bg-white border-t border-zinc-100 px-4 py-4 space-y-1 shadow-lg"
      >
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="block py-2.5 px-3 rounded-xl text-sm font-medium text-zinc-700 hover:bg-zinc-50 hover:text-emerald-600 transition-colors"
          @click="mobileOpen = false"
        >
          {{ link.label }}
        </NuxtLink>
        <div class="pt-2 flex gap-2">
          <USelectMenu
            v-model="currentLocale"
            :options="localeOptions"
            value-attribute="code"
            option-attribute="name"
            class="flex-1"
            size="sm"
          />
        </div>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
const { t, locale, locales, setLocale } = useI18n()
const auth  = useAuthStore()
const cart  = useCartStore()
const route = useRoute()

const scrolled    = ref(false)
const mobileOpen  = ref(false)
const searchOpen  = ref(false)

const siteName = 'OPPLII'

useEventListener('scroll', () => {
  scrolled.value = window.scrollY > 10
})

// Close mobile on route change
watch(() => route.path, () => { mobileOpen.value = false })

const navLinks = computed(() => [
  { to: '/products', label: t('nav.products') },
  { to: '/blog',     label: t('nav.blog') },
  { to: '/faq',      label: t('nav.faq') },
  { to: '/pages/about-us', label: t('nav.about') },
  { to: '/contact',  label: t('nav.contact') },
])

// i18n
const localeOptions = computed(() =>
  (locales.value as any[]).map(l => ({ code: l.code, name: l.name }))
)
const currentLocale = computed({
  get: () => locale.value,
  set: (v) => setLocale(v),
})

// Account menu
const accountMenuItems = computed(() => [[
  { label: t('nav.orders'),  icon: 'i-heroicons-shopping-bag', to: '/orders' },
  { label: t('nav.account'), icon: 'i-heroicons-user',         to: '/account' },
  { label: t('nav.wishlist'),icon: 'i-heroicons-heart',        to: '/wishlist' },
], [
  {
    label: t('nav.signOut'),
    icon:  'i-heroicons-arrow-left-on-rectangle',
    click: () => { auth.logout(); navigateTo('/') },
  },
]])

// Banners
const { data: banners } = await useAsyncData('header-banners', () =>
  useApi().getBanners().catch(() => []) as Promise<any[]>
, { default: () => [] })
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-to     { opacity: 0; transform: translateY(-8px); }

:deep(.container-store) { @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8; }
</style>
