<template>
  <div class="container-store py-10 max-w-2xl">
    <h1 class="font-head text-3xl font-bold text-zinc-900 mb-8">My Account</h1>

    <div class="space-y-5">
      <!-- ── Profile ── -->
      <UCard class="rounded-2xl">
        <h2 class="font-head font-semibold text-lg text-zinc-900 mb-5">Profile</h2>
        <form class="space-y-4" @submit.prevent="saveProfile">
          <div class="grid sm:grid-cols-2 gap-4">
            <UFormGroup label="Full Name">
              <UInput v-model="profile.full_name" />
            </UFormGroup>
            <UFormGroup label="Phone">
              <UInput v-model="profile.phone" type="tel" />
            </UFormGroup>
          </div>
          <UFormGroup label="Email">
            <UInput v-model="profile.email" type="email" disabled />
          </UFormGroup>
          <UFormGroup label="Language">
            <USelect v-model="profile.language_code" :options="langOptions" />
          </UFormGroup>

          <UDivider label="Change Password (optional)" class="my-4" />

          <UFormGroup label="Current Password">
            <UInput v-model="profile.current_password" type="password" />
          </UFormGroup>
          <div class="grid sm:grid-cols-2 gap-4">
            <UFormGroup label="New Password">
              <UInput v-model="profile.new_password" type="password" placeholder="Min. 8 characters" />
            </UFormGroup>
            <UFormGroup label="Confirm New Password">
              <UInput v-model="profile.confirm_password" type="password" />
            </UFormGroup>
          </div>

          <div class="flex justify-end">
            <UButton type="submit" :loading="savingProfile">Save Changes</UButton>
          </div>
        </form>
      </UCard>

      <!-- ── Saved Addresses ── -->
      <UCard class="rounded-2xl">
        <div class="flex items-center justify-between mb-5">
          <h2 class="font-head font-semibold text-lg text-zinc-900">Saved Addresses</h2>
          <UButton size="sm" variant="outline" @click="openAddrForm()">
            <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-1" />
            Add Address
          </UButton>
        </div>

        <!-- Address list -->
        <div v-if="addresses.length" class="space-y-3">
          <div
            v-for="addr in addresses"
            :key="addr.id"
            class="border rounded-2xl p-4 relative transition-colors"
            :class="addr.is_default ? 'border-emerald-300 bg-emerald-50' : 'border-zinc-200'"
          >
            <!-- Default badge -->
            <div v-if="addr.is_default"
              class="absolute top-3 right-3 text-xs font-semibold bg-emerald-500 text-white px-2 py-0.5 rounded-full">
              Default
            </div>

            <p class="font-semibold text-zinc-900 text-sm">{{ addr.full_name }}</p>
            <p class="text-sm text-zinc-600 mt-1">
              {{ addr.address_line1 }}
              <span v-if="addr.address_line2">, {{ addr.address_line2 }}</span>
            </p>
            <p class="text-sm text-zinc-600">
              {{ addr.city }},
              {{ addr.state_code || addr.state_name }}
              {{ addr.postal_code }}
            </p>
            <p class="text-sm text-zinc-600">{{ addr.country_code }}</p>
            <p v-if="addr.phone" class="text-xs text-zinc-400 mt-1">{{ addr.phone }}</p>

            <!-- Actions -->
            <div class="flex items-center gap-3 mt-3">
              <button
                v-if="!addr.is_default"
                class="text-xs text-emerald-600 hover:underline"
                @click="setDefault(addr.id)"
              >
                Set as default
              </button>
              <button
                class="text-xs text-zinc-400 hover:text-zinc-700"
                @click="openAddrForm(addr)"
              >
                Edit
              </button>
              <button
                class="text-xs text-red-400 hover:text-red-600"
                @click="deleteAddr(addr.id)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div v-else class="text-sm text-zinc-400 text-center py-6">
          No saved addresses yet.
        </div>
      </UCard>
    </div>

    <!-- ── Address form modal ── -->
    <UModal v-model="showAddrModal">
      <UCard class="rounded-2xl">
        <template #header>
          <h3 class="font-head font-semibold text-zinc-900">
            {{ editingAddr ? 'Edit Address' : 'New Address' }}
          </h3>
        </template>

        <div class="space-y-4">
          <div class="grid sm:grid-cols-2 gap-4">
            <UFormGroup label="Full Name *">
              <UInput v-model="addrForm.full_name" placeholder="John Doe" />
            </UFormGroup>
            <UFormGroup label="Phone">
              <UInput v-model="addrForm.phone" type="tel" placeholder="+1 555 0100" />
            </UFormGroup>
          </div>

          <UFormGroup label="Country *">
            <USelect
              v-model="addrForm.country_code"
              :options="countries"
              value-attribute="code"
              option-attribute="name"
              placeholder="Select country"
              @change="onCountryChange"
            />
          </UFormGroup>

          <UFormGroup v-if="addrForm.country_code" label="State / Province">
            <USelect
              v-if="addrForm.country_code === 'US'"
              v-model="addrForm.state_code"
              :options="states"
              value-attribute="code"
              option-attribute="name"
              placeholder="Select state"
            />
            <UInput
              v-else
              v-model="addrForm.state_name"
              placeholder="State / Province"
            />
          </UFormGroup>

          <UFormGroup label="City *">
            <UInput v-model="addrForm.city" />
          </UFormGroup>

          <UFormGroup label="Address Line 1 *">
            <UInput v-model="addrForm.address_line1" placeholder="123 Main St" />
          </UFormGroup>

          <UFormGroup label="Address Line 2">
            <UInput v-model="addrForm.address_line2" placeholder="Apt, Suite, etc. (optional)" />
          </UFormGroup>

          <UFormGroup label="Postal Code *">
            <UInput v-model="addrForm.postal_code" />
          </UFormGroup>

          <div class="flex items-center gap-2">
            <UCheckbox v-model="addrForm.is_default" id="is-default" />
            <label for="is-default" class="text-sm text-zinc-600 cursor-pointer">
              Set as default address
            </label>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton variant="ghost" color="gray" @click="showAddrModal = false">Cancel</UButton>
            <UButton :loading="savingAddr" @click="saveAddress">
              {{ editingAddr ? 'Save Changes' : 'Add Address' }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { t }  = useI18n()
const auth   = useAuthStore()
const api    = useApi()
const toast  = useToast()

useHead({ title: 'My Account — MyStore' })

// ── Profile ───────────────────────────────────────────────────────────────────
const profile = reactive({
  full_name:        auth.user?.full_name || '',
  phone:            '',
  email:            auth.user?.email    || '',
  language_code:    auth.user?.language_code || 'en',
  current_password: '',
  new_password:     '',
  confirm_password: '',
})
const savingProfile = ref(false)

const langOptions = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Español' },
]

async function saveProfile() {
  if (profile.new_password && profile.new_password !== profile.confirm_password) {
    toast.add({ title: 'Passwords do not match', color: 'red' }); return
  }
  savingProfile.value = true
  try {
    const payload: any = { full_name: profile.full_name || undefined, language_code: profile.language_code }
    if (profile.new_password) {
      payload.current_password = profile.current_password
      payload.new_password     = profile.new_password
    }
    const user = await api.updateMe(payload) as any
    auth.setUser(user)
    toast.add({ title: 'Profile updated', color: 'green' })
    profile.current_password = ''
    profile.new_password     = ''
    profile.confirm_password = ''
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally { savingProfile.value = false }
}

// ── Addresses ─────────────────────────────────────────────────────────────────
const addresses    = ref<any[]>([])
const showAddrModal= ref(false)
const savingAddr   = ref(false)
const editingAddr  = ref<number | null>(null)

const addrForm = reactive({
  full_name: '', phone: '', country_code: '', state_code: '',
  state_name: '', city: '', address_line1: '', address_line2: '',
  postal_code: '', is_default: false,
})

// Countries + states
const { data: countries } = await useAsyncData('account-countries',
  () => api.shippableCountries() as Promise<any[]>,
  { default: () => [] as any[] }
)
const states = ref<any[]>([])

async function onCountryChange() {
  addrForm.state_code = ''
  addrForm.state_name = ''
  if (addrForm.country_code === 'US') {
    try { states.value = await api.shippableStates('US') as any[] } catch { states.value = [] }
  }
}

async function loadAddresses() {
  try { addresses.value = await api.listAddresses() as any[] }
  catch { addresses.value = [] }
}

function openAddrForm(addr?: any) {
  editingAddr.value = addr?.id ?? null
  Object.assign(addrForm, addr
    ? {
        full_name:     addr.full_name,
        phone:         addr.phone        || '',
        country_code:  addr.country_code,
        state_code:    addr.state_code   || '',
        state_name:    addr.state_name   || '',
        city:          addr.city,
        address_line1: addr.address_line1,
        address_line2: addr.address_line2 || '',
        postal_code:   addr.postal_code,
        is_default:    addr.is_default,
      }
    : {
        full_name: auth.user?.full_name || '', phone: '',
        country_code: '', state_code: '', state_name: '',
        city: '', address_line1: '', address_line2: '',
        postal_code: '', is_default: addresses.value.length === 0,
      }
  )
  if (addr?.country_code === 'US') onCountryChange()
  showAddrModal.value = true
}

async function saveAddress() {
  if (!addrForm.full_name || !addrForm.country_code || !addrForm.city ||
      !addrForm.address_line1 || !addrForm.postal_code) {
    toast.add({ title: 'Please fill all required fields', color: 'red' }); return
  }
  savingAddr.value = true
  try {
    const payload = {
      ...addrForm,
      state_code: addrForm.state_code || undefined,
      state_name: addrForm.state_name || undefined,
      phone:      addrForm.phone      || undefined,
      address_line2: addrForm.address_line2 || undefined,
    }
    editingAddr.value
      ? await api.updateAddress(editingAddr.value, payload)
      : await api.createAddress(payload)
    toast.add({ title: editingAddr.value ? 'Address updated' : 'Address saved', color: 'green' })
    showAddrModal.value = false
    await loadAddresses()
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally { savingAddr.value = false }
}

async function deleteAddr(id: number) {
  try {
    await api.deleteAddress(id)
    toast.add({ title: 'Address deleted', color: 'green' })
    await loadAddresses()
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  }
}

async function setDefault(id: number) {
  try {
    await api.setDefaultAddr(id)
    await loadAddresses()
    toast.add({ title: 'Default address updated', color: 'green' })
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  }
}

onMounted(loadAddresses)
</script>
