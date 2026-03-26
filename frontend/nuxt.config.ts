// @ts-ignore
// @ts-ignore
export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/i18n',
  ],

  // Auto-import components by filename only (ignore subdirectory prefix)
  // components/layout/AppHeader.vue → <AppHeader> not <LayoutAppHeader>
  components: {
    dirs: [{ path: '~/components', pathPrefix: false }],
  },

  // ── Runtime config ──────────────────────────────────────────────────────
  runtimeConfig: {
    // Server-only
    apiBaseUrl: process.env.API_BASE_URL || 'http://api:9010',
    // Exposed to client
    public: {
      apiBase:        process.env.NUXT_PUBLIC_API_BASE  ?? '',
      siteUrl:        process.env.NUXT_PUBLIC_SITE_URL  || 'http://localhost:3000',
      stripeKey:      process.env.NUXT_PUBLIC_STRIPE_KEY || '',
      airwallexKey:   process.env.NUXT_PUBLIC_AIRWALLEX_KEY || '',
      airwallexEnv:   process.env.NUXT_PUBLIC_AIRWALLEX_ENV || 'demo',
    },
  },

  // ── i18n ────────────────────────────────────────────────────────────────
  i18n: {
    locales: [
      { code: 'en', name: 'English',  iso: 'en-US', file: 'en.json' },
      { code: 'es', name: 'Español',  iso: 'es-ES', file: 'es.json' },
    ],
    defaultLocale:    'en',
    langDir:          'locales/',
    strategy:         'prefix_except_default',
    detectBrowserLanguage: {
      useCookie:      true,
      cookieKey:      'i18n_locale',
      redirectOn:     'root',
    },
  },

  // ── Nuxt UI / Tailwind ──────────────────────────────────────────────────
  // @ts-ignore — @nuxt/ui module options
  ui: {
    // @ts-ignore
    icons: ['heroicons', 'lucide'],
  },

  // ── CSS ─────────────────────────────────────────────────────────────────
  css: ['~/assets/css/main.css'],

  // ── App config ──────────────────────────────────────────────────────────
  app: {
    head: {
      charset:  'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        {
          rel:  'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel:         'preconnect',
          href:        'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel:  'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300..800&family=Sora:wght@400;600;700&display=swap',
        },
      ],
    },
  },

  // ── Nitro ───────────────────────────────────────────────────────────────
  nitro: {
    compressPublicAssets: true,
  },

  // ── TypeScript ──────────────────────────────────────────────────────────
  typescript: {
    strict: true,
    shim:   false,
  },
})
