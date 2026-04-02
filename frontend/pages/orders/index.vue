<template>
  <div class="container-store py-10 max-w-3xl">
    <div v-if="auth.isGuest" class="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6 flex items-start gap-3">
      <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-amber-800">You are viewing orders as a guest.</p>
        <p class="text-xs text-amber-700 mt-0.5">Set a password to keep access to your order history.</p>
      </div>
      <UButton size="sm" color="amber" :to="registerLink">Set Password</UButton>
    </div>
    <h1 class="font-head text-3xl font-bold text-zinc-900 mb-8">{{ $t('order.title') }}</h1>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-zinc-100 rounded-2xl animate-pulse" />
    </div>

    <div v-else-if="!orders.length" class="text-center py-16">
      <div class="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-shopping-bag" class="w-8 h-8 text-zinc-300" />
      </div>
      <p class="font-head font-semibold text-zinc-600 mb-4">{{ $t('order.empty') }}</p>
      <UButton to="/products">Shop Now</UButton>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="order in orders"
        :key="order.id"
        class="block bg-white border border-zinc-100 rounded-2xl p-5 hover:border-emerald-200 hover:shadow-sm transition-all cursor-pointer"
        role="button"
        tabindex="0"
        @click="goToOrder(order.id)"
        @keydown.enter="goToOrder(order.id)"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="font-semibold text-zinc-900 font-mono text-sm">{{ $t('order.orderNo', { no: order.order_no }) }}</p>
            <p class="text-xs text-zinc-400 mt-0.5">{{ formatDate(order.created_at) }}</p>
          </div>
          <OrderStatusBadge :status="order.status" />
        </div>

        <div class="flex items-center justify-between mt-3">
          <p class="text-sm text-zinc-500">{{ order.item_count }} item{{ order.item_count !== 1 ? 's' : '' }}</p>
          <p class="font-head font-bold text-zinc-900">${{ order.total_amount.toFixed(2) }}</p>
        </div>

        <div v-if="order.items?.length" class="mt-4 space-y-3">
          <div
            v-for="item in order.items"
            :key="item.id"
            class="flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-xl bg-zinc-100 overflow-hidden flex items-center justify-center">
              <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name" class="w-full h-full object-cover" />
              <UIcon v-else name="i-heroicons-photo" class="w-5 h-5 text-zinc-300" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-zinc-800 truncate">{{ item.product_name }}</p>
              <p v-if="item.variant_attrs" class="text-xs text-zinc-400 truncate">
                {{ formatVariant(item.variant_attrs) }}
              </p>
              <p class="text-xs text-zinc-400">Qty {{ item.quantity }}</p>
            </div>
            <UButton
              v-if="canReview(order) && item.product_id"
              size="xs"
              variant="outline"
              @click.stop="openReview(order, item)"
            >
              {{ $t('order.review') }}
            </UButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center mt-8">
      <UPagination v-model="page" :total="total" :page-count="10" />
    </div>

    <!-- Review modal -->
    <UModal v-model="showReviewModal">
      <UCard class="rounded-2xl">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="font-head font-semibold text-zinc-900">{{ $t('order.reviewTitle') }}</h3>
            <span v-if="reviewOrderNo" class="text-xs text-zinc-400">
              {{ $t('order.orderNo', { no: reviewOrderNo }) }}
            </span>
          </div>
        </template>

        <div class="space-y-4">
          <div v-if="reviewItem" class="flex items-center gap-3 bg-zinc-50 rounded-xl p-3">
            <div class="w-12 h-12 rounded-xl bg-white overflow-hidden flex items-center justify-center border border-zinc-100">
              <img v-if="reviewItem.product_image" :src="reviewItem.product_image" :alt="reviewItem.product_name" class="w-full h-full object-cover" />
              <UIcon v-else name="i-heroicons-photo" class="w-5 h-5 text-zinc-300" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-zinc-800 truncate">{{ reviewItem.product_name }}</p>
              <p v-if="reviewItem.variant_attrs" class="text-xs text-zinc-400 truncate">
                {{ formatVariant(reviewItem.variant_attrs) }}
              </p>
            </div>
          </div>

          <UFormGroup :label="$t('order.reviewRating')">
            <div class="flex items-center gap-1">
              <button
                v-for="i in 5"
                :key="i"
                type="button"
                class="transition-transform hover:scale-110"
                @click="reviewRating = i"
              >
                <UIcon
                  name="i-heroicons-star-solid"
                  class="w-5 h-5"
                  :class="i <= reviewRating ? 'text-amber-400' : 'text-zinc-200'"
                />
              </button>
              <span class="text-xs text-zinc-400 ml-2">{{ reviewRating }}/5</span>
            </div>
          </UFormGroup>

          <UFormGroup :label="$t('order.reviewContent')">
            <textarea
              v-model="reviewContent"
              class="w-full border border-zinc-200 rounded-xl p-3 text-sm text-zinc-700 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              rows="4"
              :placeholder="$t('order.reviewContentPlaceholder')"
            />
          </UFormGroup>

          <UFormGroup :label="$t('order.reviewMedia')">
            <div class="space-y-2">
              <input
                ref="mediaInput"
                type="file"
                class="hidden"
                style="display:none"
                accept="image/*,video/*"
                multiple
                @change="onMediaChange"
              />
              <div class="flex items-center gap-3">
                <UButton size="sm" variant="outline" @click="openMediaPicker">
                  {{ $t('order.reviewChooseFiles') }}
                </UButton>
                <span class="text-xs text-zinc-500">
                  {{ reviewMedia.length ? `${reviewMedia.length} selected` : $t('order.reviewNoFiles') }}
                </span>
              </div>
              <p class="text-xs text-zinc-400">{{ $t('order.reviewMediaHint') }}</p>
              <div v-if="reviewMedia.length" class="space-y-2">
                <div
                  v-for="(file, idx) in reviewMedia"
                  :key="`${file.name}-${idx}`"
                  class="flex items-center justify-between text-sm text-zinc-600 bg-zinc-50 rounded-xl px-3 py-2"
                >
                  <span class="truncate">{{ file.name }}</span>
                  <button
                    type="button"
                    class="text-xs text-red-500 hover:text-red-600"
                    @click="removeMedia(idx)"
                  >
                    {{ $t('common.delete') }}
                  </button>
                </div>
              </div>
            </div>
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton variant="ghost" color="gray" @click="closeReviewModal">
              {{ $t('common.cancel') }}
            </UButton>
            <UButton :loading="submittingReview" @click="submitReview">
              {{ $t('order.reviewSubmit') }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
definePageMeta({ middleware: 'auth-or-guest' })

const { t }    = useI18n()
const auth     = useAuthStore()
const api      = useApi()
const toast    = useToast()
const page     = ref(1)
const registerLink = computed(() => {
  const email = auth.user?.email
  return email ? `/auth/register?email=${encodeURIComponent(email)}` : '/auth/register'
})

useHead({ title: 'My Orders - OPPLII' })

const { data, pending: loading } = await useAsyncData(
  'my-orders',
  () => api.listOrders(page.value) as Promise<any>,
  { watch: [page] }
)

const orders     = computed(() => data.value?.items ?? [])
const total      = computed(() => data.value?.total ?? 0)
const totalPages = computed(() => data.value?.pages ?? 1)

function formatDate(d: string) { return dayjs(d).format('MMM D, YYYY') }

const showReviewModal = ref(false)
const submittingReview = ref(false)
const reviewOrderId = ref<number | null>(null)
const reviewOrderNo = ref<string | null>(null)
const reviewItem = ref<any | null>(null)
const reviewRating = ref(5)
const reviewContent = ref('')
const reviewMedia = ref<File[]>([])
const mediaInput = ref<HTMLInputElement | null>(null)

function canReview(order: any) {
  return !auth.isGuest && order.payment_status === 'paid'
}

function goToOrder(orderId: number) {
  navigateTo(`/orders/${orderId}`)
}

function openReview(order: any, item: any) {
  if (!canReview(order) || !item?.product_id) return
  showReviewModal.value = true
  reviewOrderId.value = order.id
  reviewOrderNo.value = order.order_no
  reviewItem.value = item
  reviewContent.value = ''
  reviewMedia.value = []
  reviewRating.value = 5
}

function closeReviewModal() {
  showReviewModal.value = false
}

function onMediaChange(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  if (!files.length) return

  const merged = [...reviewMedia.value, ...files].slice(0, 3)
  reviewMedia.value = merged

  if (mediaInput.value) {
    mediaInput.value.value = ''
  }
}

function removeMedia(idx: number) {
  reviewMedia.value.splice(idx, 1)
}

function openMediaPicker() {
  mediaInput.value?.click()
}

async function submitReview() {
  if (!reviewOrderId.value || !reviewItem.value?.product_id) {
    toast.add({ title: t('order.reviewNoItems'), color: 'red' })
    return
  }

  submittingReview.value = true
  try {
    const fd = new FormData()
    fd.append('rating', String(reviewRating.value))
    if (reviewContent.value.trim()) fd.append('content', reviewContent.value.trim())
    if (auth.displayName) fd.append('reviewer_name', auth.displayName)
    fd.append('order_id', String(reviewOrderId.value))
    reviewMedia.value.forEach((file) => fd.append('media', file))

    await api.submitReview(reviewItem.value.product_id, fd)
    toast.add({ title: t('order.reviewSubmitted'), color: 'green' })
    showReviewModal.value = false
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || t('common.error'), color: 'red' })
  } finally {
    submittingReview.value = false
  }
}

function formatVariant(attrs: Record<string, string>) {
  return Object.values(attrs).join(' / ')
}
</script>
