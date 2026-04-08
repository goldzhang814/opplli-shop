<template>
  <div class="container-store py-10">
    <h1 class="font-head text-3xl font-bold text-zinc-900 mb-8">{{ $t('checkout.title') }}</h1>

    <!-- Empty cart guard -->
    <div v-if="cart.isEmpty" class="text-center py-16">
      <p class="text-zinc-500 mb-4">Your cart is empty.</p>
      <UButton to="/products">Shop Products</UButton>
    </div>

    <div v-else class="grid lg:grid-cols-[1fr_380px] gap-10">
      <!-- ── Left: steps ─────────────────────────────────────────── -->
      <div class="space-y-6">

        <!-- Step indicator -->
        <div class="flex items-center gap-2">
          <div
            v-for="(s, i) in steps"
            :key="s.key"
            class="flex items-center gap-2"
          >
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all"
              :class="step > i
                ? 'bg-emerald-500 text-white'
                : step === i
                  ? 'bg-zinc-900 text-white'
                  : 'bg-zinc-100 text-zinc-400'"
            >
              <UIcon v-if="step > i" name="i-heroicons-check" class="w-3.5 h-3.5" />
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="text-sm font-medium" :class="step === i ? 'text-zinc-900' : 'text-zinc-400'">
              {{ s.label }}
            </span>
            <UIcon v-if="i < steps.length - 1" name="i-heroicons-chevron-right" class="w-4 h-4 text-zinc-300" />
          </div>
        </div>

        <!-- ─── Step 0: Address ──────────────────────────────────── -->
        <div v-if="step === 0">
          <!-- Guest email -->
          <div v-if="!auth.isLoggedIn" class="bg-zinc-50 rounded-2xl p-5 mb-5">
            <p class="text-sm font-semibold text-zinc-700 mb-3">{{ $t('checkout.guestEmail') }}</p>
            <div class="flex gap-3">
              <UInput v-model="guestEmail" type="email" placeholder="you@example.com" class="flex-1" />
              <UButton variant="outline" color="gray" :to="`/auth/login?redirect=/checkout`">
                {{ $t('checkout.orSignIn') }}
              </UButton>
            </div>
            <p v-if="guestEmailError" class="text-xs text-red-500 mt-1">{{ guestEmailError }}</p>
          </div>

          <!-- Saved addresses selector (logged-in users only) -->
          <div v-if="auth.isLoggedIn && savedAddresses.length" class="mb-5">
            <p class="text-sm font-semibold text-zinc-700 mb-3">Saved Addresses</p>
            <div class="grid sm:grid-cols-2 gap-3 mb-3">
              <button
                v-for="addr in savedAddresses"
                :key="addr.id"
                class="text-left border-2 rounded-2xl p-4 transition-all"
                :class="selectedAddrId === addr.id
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-zinc-200 hover:border-zinc-300'"
                @click="applySavedAddress(addr)"
              >
                <div class="flex items-start justify-between">
                  <p class="font-medium text-zinc-900 text-sm">{{ addr.full_name }}</p>
                  <span v-if="addr.is_default"
                    class="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-medium ml-2 flex-shrink-0">
                    Default
                  </span>
                </div>
                <p class="text-xs text-zinc-500 mt-1">{{ addr.address_line1 }}</p>
                <p class="text-xs text-zinc-500">{{ addr.city }}, {{ addr.state_code || addr.state_name }} {{ addr.postal_code }}</p>
                <p class="text-xs text-zinc-500">{{ addr.country_code }}</p>
              </button>
            </div>
            <button
              class="text-sm text-emerald-600 hover:underline"
              @click="selectedAddrId = null; clearAddress()"
            >
              + Use a different address
            </button>
          </div>

          <UCard class="rounded-2xl">
            <h2 class="font-head font-semibold text-lg text-zinc-900 mb-5">{{ $t('checkout.address') }}</h2>

            <div class="space-y-4">
              <div class="grid sm:grid-cols-2 gap-4">
                <UFormGroup :label="$t('checkout.fullName')" :error="errors.full_name">
                  <UInput v-model="address.full_name" autocomplete="name" />
                </UFormGroup>
                <UFormGroup :label="$t('checkout.phone')">
                  <UInput v-model="address.phone" type="tel" autocomplete="tel" />
                </UFormGroup>
              </div>

              <UFormGroup :label="$t('checkout.country')" :error="errors.country_code">
                <USelect
                  v-model="address.country_code"
                  :options="countries"
                  value-attribute="code"
                  option-attribute="name"
                  :placeholder="loadingCountries ? 'Loading…' : 'Select country'"
                  @change="onCountryChange"
                />
              </UFormGroup>

              <!-- State: dropdown for US, free text otherwise -->
              <UFormGroup v-if="address.country_code" :label="$t('checkout.state')">
                <USelect
                  v-if="address.country_code === 'US'"
                  v-model="address.state_code"
                  :options="states"
                  value-attribute="code"
                  option-attribute="name"
                  placeholder="Select state"
                />
                <UInput
                  v-else
                  v-model="address.state_name"
                  :placeholder="$t('checkout.state')"
                />
              </UFormGroup>

              <UFormGroup :label="$t('checkout.city')" :error="errors.city">
                <UInput v-model="address.city" autocomplete="address-level2" />
              </UFormGroup>

              <UFormGroup :label="$t('checkout.address1')" :error="errors.address_line1">
                <UInput v-model="address.address_line1" autocomplete="address-line1" />
              </UFormGroup>

              <UFormGroup :label="$t('checkout.address2')">
                <UInput v-model="address.address_line2" autocomplete="address-line2" />
              </UFormGroup>

              <UFormGroup :label="$t('checkout.postalCode')" :error="errors.postal_code">
                <UInput v-model="address.postal_code" autocomplete="postal-code" />
              </UFormGroup>

              <!-- Shipping estimate preview -->
              <div v-if="shippingEstimate" class="bg-emerald-50 rounded-xl p-4 text-sm">
                <div v-if="shippingEstimate.deliverable">
                  <div class="flex justify-between">
                    <span class="text-zinc-600">Shipping ({{ shippingEstimate.zone_name }})</span>
                    <span class="font-semibold text-zinc-900">
                      {{ shippingEstimate.shipping_fee === 0 ? 'Free' : `$${shippingEstimate.shipping_fee.toFixed(2)}` }}
                    </span>
                  </div>
                  <p v-if="shippingEstimate.remaining_for_free" class="text-emerald-600 text-xs mt-1">
                    {{ $t('cart.spendMore', { amount: shippingEstimate.remaining_for_free.toFixed(2) }) }}
                  </p>
                </div>
                <p v-else class="text-red-600">{{ shippingEstimate.message }}</p>
              </div>

              <div class="flex items-center gap-2">
                <UCheckbox v-model="saveAddress" id="save-addr" />
                <label for="save-addr" class="text-sm text-zinc-600 cursor-pointer">
                  {{ $t('checkout.saveAddress') }}
                </label>
              </div>
            </div>

            <div class="mt-6">
              <UButton size="lg" block :loading="previewLoading" @click="goToPayment">
                Continue to Payment →
              </UButton>
            </div>
          </UCard>
        </div>

        <!-- ─── Step 1: Payment ──────────────────────────────────── -->
        <div v-if="step === 1">
          <UCard class="rounded-2xl">
            <h2 class="font-head font-semibold text-lg text-zinc-900 mb-5">{{ $t('checkout.payment') }}</h2>

            <!-- Payment method selector -->
            <div class="grid sm:grid-cols-3 gap-3 mb-6">
              <button
                v-for="pm in paymentMethods"
                :key="pm.value"
                class="flex flex-col items-center gap-2 border-2 rounded-2xl p-4 transition-all"
                :class="paymentMethod === pm.value
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-zinc-200 hover:border-zinc-300'"
                @click="paymentMethod = pm.value"
              >
                <span class="text-2xl">{{ pm.icon }}</span>
                <span class="text-sm font-medium text-zinc-700">{{ pm.label }}</span>
              </button>
            </div>

            <!-- Coupon code -->
            <div class="mb-6">
              <p class="text-sm font-medium text-zinc-700 mb-2">{{ $t('checkout.coupon') }}</p>
              <div class="flex gap-2">
                <UInput
                  v-model="couponCode"
                  :placeholder="$t('checkout.coupon')"
                  class="flex-1"
                  :disabled="!!appliedCoupon"
                />
                <UButton
                  v-if="!appliedCoupon"
                  variant="outline"
                  color="gray"
                  :loading="couponLoading"
                  @click="applyCoupon"
                >
                  {{ $t('checkout.applyCoupon') }}
                </UButton>
                <UButton
                  v-else
                  variant="ghost"
                  color="red"
                  @click="removeCoupon"
                >
                  Remove
                </UButton>
              </div>
              <p v-if="appliedCoupon" class="text-sm text-emerald-600 mt-1.5 flex items-center gap-1">
                <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
                {{ $t('checkout.couponApplied') }} — Save ${{ appliedCoupon.discount_amount?.toFixed(2) }}
              </p>
              <p v-if="couponError" class="text-sm text-red-500 mt-1">{{ couponError }}</p>
            </div>

            <!-- Terms -->
            <div class="flex items-start gap-2 mb-6">
              <UCheckbox v-model="agreedTerms" id="terms" />
              <label for="terms" class="text-xs text-zinc-500 cursor-pointer leading-relaxed">
                {{ $t('checkout.agree') }}
                <NuxtLink to="/pages/terms-of-service" target="_blank" class="text-emerald-600 hover:underline">Terms</NuxtLink>
                and
                <NuxtLink to="/pages/privacy-policy" target="_blank" class="text-emerald-600 hover:underline">Privacy Policy</NuxtLink>.
              </label>
            </div>
            <p class="text-xs text-zinc-500 mb-4">
              All orders placed through this checkout are governed by the laws of the Hong Kong Special Administrative Region.
            </p>

            <div class="flex gap-3">
              <UButton variant="ghost" color="gray" @click="step--">← Back</UButton>
              <UButton
                size="lg"
                class="flex-1"
                :loading="placingOrder"
                :disabled="!agreedTerms"
                @click="placeOrder"
              >
                {{ $t('checkout.placeOrder') }}
              </UButton>
            </div>
          </UCard>
        </div>

        <!-- ─── Step 2: Processing / Success ────────────────────── -->
        <div v-if="step === 2">
          <UCard class="rounded-2xl text-center py-10">
            <div v-if="paymentProcessing" class="space-y-4">
              <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
                <UIcon name="i-heroicons-lock-closed" class="w-8 h-8 text-emerald-600" />
              </div>
              <h2 class="font-head text-xl font-bold text-zinc-900">Processing Payment</h2>
              <p class="text-zinc-500 text-sm">Please wait while we securely process your payment…</p>
              <div class="flex justify-center">
                <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-emerald-500 animate-spin" />
              </div>
            </div>

            <!-- Stripe card element -->
            <div v-else-if="paymentMethod === 'stripe' && stripeClientSecret" class="text-left space-y-5">
              <h2 class="font-head text-xl font-bold text-zinc-900">Complete Payment</h2>
              <div id="stripe-card-element" class="border border-zinc-200 rounded-xl p-4 min-h-[44px]" />
              <p v-if="stripeError" class="text-sm text-red-500">{{ stripeError }}</p>
              <UButton size="lg" block :loading="confirmingPayment" @click="confirmStripe">
                Pay ${{ preview?.total_amount.toFixed(2) }}
              </UButton>
            </div>

            <!-- PayPal redirect -->
            <div v-else-if="paymentMethod === 'paypal' && paypalApprovalUrl">
              <h2 class="font-head text-xl font-bold text-zinc-900 mb-4">Redirecting to PayPal</h2>
              <p class="text-zinc-500 text-sm mb-5">You'll be redirected to PayPal to complete your payment.</p>
              <UButton size="lg" :to="paypalApprovalUrl" external>
                Continue to PayPal →
              </UButton>
            </div>

            <div v-else-if="paymentMethod === 'airwallex' && airwallexClientSecret" class="text-left space-y-5">
              <h2 class="font-head text-xl font-bold text-zinc-900">Complete Payment</h2>
              <p class="text-sm text-zinc-500">
                Enter your card details below to complete the Airwallex payment.
              </p>
              <div id="airwallex-card" class="border border-zinc-200 rounded-xl p-4 min-h-[44px]" />
              <div id="airwallex-auth" class="min-h-0" />
              <p v-if="airwallexStatusText" class="text-sm text-zinc-500">{{ airwallexStatusText }}</p>
              <p v-if="airwallexError" class="text-sm text-red-500">{{ airwallexError }}</p>
              <UButton size="lg" block :loading="confirmingPayment" @click="confirmAirwallex">
                Pay ${{ preview?.total_amount.toFixed(2) }}
              </UButton>
            </div>
          </UCard>
        </div>
      </div>

      <!-- ── Right: Order summary ──────────────────────────────── -->
      <div class="space-y-4">
        <UCard class="rounded-2xl">
          <h2 class="font-head font-semibold text-zinc-900 mb-4">{{ $t('checkout.orderSummary') }}</h2>

          <!-- Items -->
          <div class="space-y-3 mb-4">
            <div v-for="item in cart.items" :key="item.sku_id" class="flex gap-3">
              <div class="w-14 h-14 rounded-xl bg-zinc-100 overflow-hidden flex-shrink-0">
                <img v-if="item.cover_image" :src="item.cover_image" :alt="item.product_name" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center text-xl">🌿</div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-zinc-900 line-clamp-1">{{ item.product_name }}</p>
                <p v-if="item.variant_attrs" class="text-xs text-zinc-400">
                  {{ Object.values(item.variant_attrs).join(' / ') }}
                </p>
                <p class="text-xs text-zinc-500">Qty: {{ item.quantity }}</p>
              </div>
              <p class="text-sm font-semibold text-zinc-900 flex-shrink-0">${{ item.subtotal.toFixed(2) }}</p>
            </div>
          </div>

          <div class="border-t border-zinc-100 pt-4 space-y-2.5 text-sm">
            <div class="flex justify-between text-zinc-600">
              <span>{{ $t('cart.subtotal') }}</span>
              <span>${{ (preview?.subtotal ?? cart.subtotal).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-zinc-600">
              <span>{{ $t('checkout.shippingFee') }}</span>
              <span>
                {{ (preview?.shipping_fee ?? 0) === 0 ? $t('common.free') : `$${(preview?.shipping_fee ?? 0).toFixed(2)}` }}
              </span>
            </div>
            <div class="flex justify-between text-zinc-600">
              <span>{{ $t('checkout.tax') }}</span>
              <span>${{ (preview?.tax_amount ?? 0).toFixed(2) }}</span>
            </div>
            <div v-if="(preview?.discount_amount ?? 0) > 0" class="flex justify-between text-emerald-600">
              <span>{{ $t('checkout.discount') }}</span>
              <span>-${{ (preview?.discount_amount ?? 0).toFixed(2) }}</span>
            </div>
            <div class="border-t border-zinc-100 pt-2.5 flex justify-between">
              <span class="font-head font-bold text-zinc-900">{{ $t('checkout.total') }}</span>
              <span class="font-head font-bold text-xl text-zinc-900">
                ${{ (preview?.total_amount ?? cart.subtotal).toFixed(2) }}
              </span>
            </div>
          </div>
        </UCard>

        <!-- Security badges -->
        <div class="flex items-center justify-center gap-4 text-xs text-zinc-400">
          <div class="flex items-center gap-1">
            <UIcon name="i-heroicons-lock-closed" class="w-3.5 h-3.5 text-emerald-500" />
            SSL Encrypted
          </div>
          <div class="flex items-center gap-1">
            <UIcon name="i-heroicons-shield-check" class="w-3.5 h-3.5 text-emerald-500" />
            Secure Payment
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const auth          = useAuthStore()
const cart          = useCartStore()
const api           = useApi()
const config        = useRuntimeConfig()
const toast         = useToast()
const route         = useRoute()

useHead({ title: `Checkout — OPPLII` })

// ── State ──────────────────────────────────────────────────────────────────
// ── Saved addresses ──────────────────────────────────────────────────────────
const savedAddresses = ref<any[]>([])
const selectedAddrId = ref<number | null>(null)

async function loadSavedAddresses() {
  if (!auth.isLoggedIn) return
  try {
    savedAddresses.value = await api.listAddresses() as any[]
    // Auto-select default address
    const def = savedAddresses.value.find(a => a.is_default)
    if (def) applySavedAddress(def)
  } catch { savedAddresses.value = [] }
}

function applySavedAddress(addr: any) {
  selectedAddrId.value   = addr.id
  address.full_name      = addr.full_name
  address.phone          = addr.phone          || ''
  address.country_code   = addr.country_code
  address.state_code     = addr.state_code     || ''
  address.state_name     = addr.state_name     || ''
  address.city           = addr.city
  address.address_line1  = addr.address_line1
  address.address_line2  = addr.address_line2  || ''
  address.postal_code    = addr.postal_code
  // Load states if US
  if (addr.country_code === 'US') {
    api.shippableStates('US').then((s: any) => { states.value = s }).catch(() => {})
  }
  fetchShippingEstimate()
}

function clearAddress() {
  Object.keys(address).forEach(k => { (address as any)[k] = '' })
  shippingEstimate.value = null
}

// ── Step state ────────────────────────────────────────────────────────────────
const step          = ref(0)
const guestEmail    = ref('')
const guestEmailError = ref('')
const guestAuthInFlight = ref(false)
const guestAuthEmail = ref('')
const saveAddress   = ref(auth.isLoggedIn)
const paymentMethod = ref<'stripe' | 'paypal' | 'airwallex'>('stripe')
const couponCode    = ref('')
const couponError   = ref('')
const couponLoading = ref(false)
const appliedCoupon = ref<any>(null)
const agreedTerms   = ref(false)
const placingOrder  = ref(false)
const previewLoading= ref(false)
const preview       = ref<any>(null)

// Payment state
const orderId             = ref<number | null>(null)
const orderNo             = ref('')
const stripeClientSecret  = ref('')
const airwallexClientSecret = ref('')
const airwallexIntentId   = ref('')
const paypalApprovalUrl   = ref('')
const stripeError         = ref('')
const airwallexError      = ref('')
const airwallexStatusText = ref('')
const airwallexReady      = ref(false)
const confirmingPayment   = ref(false)
const paymentProcessing   = ref(false)

const address = reactive({
  full_name:     '',
  phone:         '',
  country_code:  '',
  state_code:    '',
  state_name:    '',
  city:          '',
  address_line1: '',
  address_line2: '',
  postal_code:   '',
})

const errors = reactive({
  full_name: '', country_code: '', city: '', address_line1: '', postal_code: '',
})

// ── Countries + states ────────────────────────────────────────────────────
const loadingCountries = ref(true)
const { data: countries } = await useAsyncData('checkout-countries',
  () => api.shippableCountries() as Promise<any[]>,
  { default: () => [] }
)
loadingCountries.value = false

const { data: states, refresh: refreshStates } = await useAsyncData(
  'checkout-states',
  () => address.country_code === 'US'
    ? api.shippableStates('US') as Promise<any[]>
    : Promise.resolve([]),
  { default: () => [] }
)

const shippingEstimate = ref<any>(null)

const { $getChannelRef } = useNuxtApp()

async function onCountryChange() {
  address.state_code  = ''
  address.state_name  = ''
  shippingEstimate.value = null
  await refreshStates()
  if (address.country_code) {
    fetchShippingEstimate()
  }
}

const fetchShippingEstimate = useDebounceFn(async () => {
  if (!address.country_code) return
  try {
    shippingEstimate.value = await api.shippingEstimate({
      country_code: address.country_code,
      state_code:   address.state_code || undefined,
      subtotal:     cart.subtotal,
    })
  } catch { /* silent */ }
}, 500)

watch(() => [address.state_code, address.state_name], fetchShippingEstimate)

watch(guestEmail, () => {
  if (guestEmail.value) guestEmailError.value = ''
})

const debouncedGuestAuth = useDebounceFn(async () => {
  if (auth.token) return
  if (!guestEmail.value) return
  if (guestAuthInFlight.value) return
  if (guestAuthEmail.value === guestEmail.value) return
  guestAuthInFlight.value = true
  const ok = await ensureGuestAuth()
  if (ok) guestAuthEmail.value = guestEmail.value
  guestAuthInFlight.value = false
}, 600)

watch(guestEmail, (val) => {
  if (guestAuthEmail.value && val && val !== guestAuthEmail.value) {
    auth.logout()
    guestAuthEmail.value = ''
  }
  debouncedGuestAuth()
})

watch(paymentMethod, () => {
  stripeClientSecret.value = ''
  stripeError.value = ''
  paypalApprovalUrl.value = ''
  airwallexClientSecret.value = ''
  airwallexIntentId.value = ''
  airwallexError.value = ''
  airwallexStatusText.value = ''
  airwallexReady.value = false

  if (cardElement?.unmount) {
    cardElement.unmount()
    cardElement = null
  }

  if (airwallexCardElement?.destroy) {
    airwallexCardElement.destroy()
    airwallexCardElement = null
  }
})

// ── Coupon ────────────────────────────────────────────────────────────────
async function applyCoupon() {
  couponError.value   = ''
  couponLoading.value = true
  try {
    const res = await api.validateCoupon({
      code:        couponCode.value,
      order_total: cart.subtotal,
    }) as any
    if (res.valid) {
      appliedCoupon.value = res
      await refreshPreview(appliedCoupon.value?.code)
      toast.add({ title: t('checkout.couponApplied'), color: 'green' })
    } else {
      couponError.value = res.message
    }
  } catch { couponError.value = t('common.error') }
  finally { couponLoading.value = false }
}

async function removeCoupon() {
  appliedCoupon.value = null
  couponCode.value    = ''
  couponError.value   = ''
  await refreshPreview()
}

async function refreshPreview(couponCode?: string | null) {
  try {
    preview.value = await api.checkoutPreview({
      address:     { ...address },
      coupon_code: couponCode || undefined,
    })
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  }
}

// ── Validate address ──────────────────────────────────────────────────────
function validateAddress(): boolean {
  let ok = true
  const required: (keyof typeof errors)[] = ['full_name', 'country_code', 'city', 'address_line1', 'postal_code']
  required.forEach(k => {
    errors[k] = (address as any)[k] ? '' : 'Required'
    if ((address as any)[k] === '') ok = false
  })
  return ok
}

// ── Steps ─────────────────────────────────────────────────────────────────
const steps = computed(() => [
  { key: 'address', label: t('checkout.shipping') },
  { key: 'payment', label: t('checkout.payment') },
  { key: 'confirm', label: t('checkout.review') },
])

const paymentMethods: Array<{ value: 'stripe' | 'paypal' | 'airwallex'; icon: string; label: string }> = [
  // { value: 'stripe',    icon: '💳', label: 'Card' }, todo等待开放
  // { value: 'paypal',    icon: '🅿️',  label: 'PayPal' },todo等待开放
  { value: 'airwallex', icon: '🌐', label: 'Airwallex' },
]

async function goToPayment() {
  if (!validateAddress()) return
  if (!auth.token) {
    const ok = await ensureGuestAuth()
    if (!ok) return
  }
  previewLoading.value = true
  try {
    preview.value = await api.checkoutPreview({
      address:     { ...address },
      coupon_code: appliedCoupon.value?.code || undefined,
    })
    if (!preview.value.shipping?.deliverable) {
      toast.add({ title: preview.value.shipping?.message || 'Region not supported', color: 'red' })
      return
    }
    step.value = 1
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally {
    previewLoading.value = false
  }
}

async function ensureGuestAuth(): Promise<boolean> {
  if (auth.token) return true
  if (!guestEmail.value) {
    guestEmailError.value = 'Email is required for guest checkout.'
    toast.add({ title: guestEmailError.value, color: 'red' })
    return false
  }
  guestEmailError.value = ''
  try {
    const res = await api.guestCheckout({ email: guestEmail.value }) as any
    auth.setToken(res.access_token)
    const user = await api.me() as any
    auth.setUser(user)
    return true
  } catch (e: any) {
    const msg = e?.data?.detail || e?.message || t('common.error')
    toast.add({ title: msg, color: 'red' })
    return false
  }
}

async function placeOrder() {
  if (!agreedTerms.value) return
  if (!auth.token) {
    const ok = await ensureGuestAuth()
    if (!ok) return
  }
  placingOrder.value = true
  try {
    stripeClientSecret.value = ''
    paypalApprovalUrl.value = ''
    stripeError.value = ''
    airwallexClientSecret.value = ''
    airwallexIntentId.value = ''
    airwallexError.value = ''
    airwallexStatusText.value = ''
    airwallexReady.value = false

    const res = await api.placeOrder({
      address:        { ...address },
      payment_method: paymentMethod.value,
      coupon_code:    appliedCoupon.value?.code || undefined,
      language_code:  locale.value,
      save_address:   saveAddress.value,
      channel_ref: $getChannelRef()
    }) as any

    orderId.value = res.order_id
    orderNo.value = res.order_no
    step.value    = 2
    paymentProcessing.value = true

    // Init payment
    if (paymentMethod.value === 'stripe') {
      const piRes = await api.initStripe(res.order_id) as any
      stripeClientSecret.value = piRes.client_secret
      await mountStripeElements()
      paymentProcessing.value = false

    } else if (paymentMethod.value === 'paypal') {
      const ppRes = await api.initPayPal(res.order_id) as any
      paypalApprovalUrl.value = ppRes.approval_url
      paymentProcessing.value = false

    } else if (paymentMethod.value === 'airwallex') {
      const awRes = await api.initAirwallex(res.order_id) as any

      airwallexIntentId.value =
        awRes.payment_intent_id || awRes.intent_id || awRes.id || ''
      airwallexClientSecret.value =
        awRes.client_secret || awRes.payment_intent_client_secret || ''

      if (!airwallexIntentId.value || !airwallexClientSecret.value) {
        throw new Error('Airwallex init response missing payment_intent_id or client_secret')
      }

      paymentProcessing.value = false
      await nextTick()
      await mountAirwallexElements()
    }
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || e?.message || t('common.error'), color: 'red' })
    paymentProcessing.value = false
    step.value = 1
  } finally {
    placingOrder.value = false
  }
}

// ── Stripe Elements ───────────────────────────────────────────────────────
let stripeInstance: any = null
let stripeElements: any = null
let cardElement: any    = null
let airwallexSdkPromise: Promise<any> | null = null
let airwallexCardElement: any = null

async function mountStripeElements() {
  if (!import.meta.client) return
  const { loadStripe } = await import('@stripe/stripe-js')
  stripeInstance = await loadStripe(config.public.stripeKey)
  stripeElements = stripeInstance.elements({ clientSecret: stripeClientSecret.value })
  cardElement    = stripeElements.create('card', {
    style: {
      base: { fontFamily: 'Plus Jakarta Sans, system-ui', fontSize: '15px', color: '#18181b' },
    },
  })
  await nextTick()
  cardElement.mount('#stripe-card-element')
}

function getAirwallexLocale() {
  return locale.value === 'es' ? 'es' : 'en'
}

async function loadAirwallexSdk() {
  if (!import.meta.client) return null

  const awWindow = window as Window & { AirwallexComponentsSDK?: any }
  if (awWindow.AirwallexComponentsSDK) {
    return awWindow.AirwallexComponentsSDK
  }

  if (!airwallexSdkPromise) {
    airwallexSdkPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector('script[data-airwallex-sdk="true"]') as HTMLScriptElement | null
      if (existing) {
        existing.addEventListener('load', () => resolve(awWindow.AirwallexComponentsSDK))
        existing.addEventListener('error', () => reject(new Error('Failed to load Airwallex SDK')))
        return
      }

      const script = document.createElement('script')
      script.src = 'https://static.airwallex.com/components/sdk/v1/index.js'
      script.async = true
      script.dataset.airwallexSdk = 'true'
      script.onload = () => resolve(awWindow.AirwallexComponentsSDK)
      script.onerror = () => reject(new Error('Failed to load Airwallex SDK'))
      document.head.appendChild(script)
    })
  }

  return airwallexSdkPromise
}

async function waitForElement(id: string, timeout = 4000) {
  const startedAt = Date.now()

  while (Date.now() - startedAt < timeout) {
    const el = document.getElementById(id)
    if (el) return el
    await new Promise(resolve => window.setTimeout(resolve, 50))
  }

  return null
}

async function mountAirwallexElements() {
  if (!import.meta.client) return

  const sdk = await loadAirwallexSdk()
  if (!sdk) throw new Error('Airwallex SDK unavailable')

  await sdk.init({
    env: config.public.airwallexEnv === 'prod' ? 'prod' : 'demo',
    enabledElements: ['payments'],
    locale: getAirwallexLocale(),
  })

  await nextTick()
  airwallexReady.value = false
  airwallexStatusText.value = 'Loading secure card fields...'

  if (airwallexCardElement?.destroy) {
    airwallexCardElement.destroy()
  }

  airwallexCardElement = await sdk.createElement('card', {
    authFormContainer: 'airwallex-auth',
    popupWidth: 420,
    popupHeight: 640,
    style: {
      base: {
        color: '#18181b',
        fontFamily: 'Plus Jakarta Sans, system-ui',
        fontSize: '15px',
        '::placeholder': { color: '#71717a' },
      },
    },
  })

  airwallexCardElement.on?.('ready', () => {
    airwallexReady.value = true
    airwallexStatusText.value = 'Card fields ready.'
  })

  airwallexCardElement.on?.('focus', () => {
    airwallexStatusText.value = ''
  })

  airwallexCardElement.on?.('error', (event: any) => {
    airwallexError.value =
      event?.detail?.error?.message ||
      event?.detail?.message ||
      'Failed to load Airwallex card fields.'
    airwallexStatusText.value = ''
  })

  const cardContainer = await waitForElement('airwallex-card')
  if (!cardContainer) {
    throw new Error('Airwallex card container not found')
  }

  airwallexCardElement.mount(cardContainer)
  airwallexReady.value = true
  airwallexStatusText.value = ''

  window.setTimeout(() => {
    if (!airwallexReady.value && !airwallexError.value) {
      airwallexStatusText.value = 'Card fields are taking longer than expected to load.'
    }
  }, 4000)
}

async function confirmAirwallex() {
  if (!airwallexCardElement || !airwallexIntentId.value || !airwallexClientSecret.value) return

  confirmingPayment.value = true
  airwallexError.value = ''
  airwallexStatusText.value = 'Submitting payment...'

  try {
    const response = await airwallexCardElement.confirm({
      intent_id: airwallexIntentId.value,
      client_secret: airwallexClientSecret.value,
    })

    const status = response?.status || response?.payment_intent?.status
    if (status === 'SUCCEEDED') {
      airwallexStatusText.value = 'Payment completed.'
      await navigateTo(`/orders/${orderId.value}?success=1`)
      return
    }

    if (status === 'REQUIRES_CUSTOMER_ACTION') {
      airwallexStatusText.value = 'Additional verification required. Please complete the authentication step.'
      return
    }

    if (status === 'PENDING' || status === 'REQUIRES_PAYMENT_METHOD') {
      airwallexStatusText.value = 'Payment is still processing. Please wait a moment.'
    } else {
      airwallexError.value =
        response?.message ||
        response?.latest_payment_attempt?.failure_reason ||
        response?.payment_intent?.latest_payment_attempt?.failure_reason ||
        'Airwallex payment was not completed.'
      airwallexStatusText.value = ''
    }
  } catch (e: any) {
    airwallexError.value =
      e?.message ||
      e?.error?.message ||
      e?.data?.message ||
      'Airwallex payment failed.'
    airwallexStatusText.value = ''
  } finally {
    confirmingPayment.value = false
  }
}

async function confirmStripe() {
  if (!stripeInstance || !cardElement) return
  confirmingPayment.value = true
  stripeError.value       = ''
  try {
    const { error, paymentIntent } = await stripeInstance.confirmCardPayment(
      stripeClientSecret.value,
      { payment_method: { card: cardElement } }
    )
    if (error) {
      stripeError.value = error.message
    } else if (paymentIntent.status === 'succeeded') {
      await navigateTo(`/orders/${orderId.value}?success=1`)
    }
  } finally {
    confirmingPayment.value = false
  }
}

// ── Channel tracking ──────────────────────────────────────────────────────
onMounted(async () => {
  const ref = route.query.ref as string
  if (ref) api.track(ref, 'visit')
  await loadSavedAddresses()
})

onBeforeUnmount(() => {
  if (cardElement?.unmount) cardElement.unmount()
  if (airwallexCardElement?.destroy) airwallexCardElement.destroy()
})
</script>
