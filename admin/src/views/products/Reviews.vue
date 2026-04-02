<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">Reviews</h2>
      <p class="page-sub">{{ total }} reviews</p>
    </div>
    <n-card :bordered="false" style="border-radius:14px; margin-bottom:16px">
      <n-radio-group v-model:value="statusFilter" @update:value="load">
        <n-radio-button value="">All</n-radio-button>
        <n-radio-button value="pending">Pending</n-radio-button>
        <n-radio-button value="approved">Approved</n-radio-button>
        <n-radio-button value="rejected">Rejected</n-radio-button>
      </n-radio-group>
    </n-card>
    <n-card :bordered="false" style="border-radius:14px">
      <div v-if="loading" style="padding:40px;text-align:center"><n-spin /></div>
      <div v-else-if="!reviews.length" style="padding:40px;text-align:center;color:#9ca3af">No reviews</div>
      <div v-else>
        <div v-for="r in reviews" :key="r.id" style="display:flex;gap:16px;padding:16px 0;border-bottom:1px solid #f3f4f6">
          <div style="width:130px;flex-shrink:0">
            <div style="display:flex;gap:2px;margin-bottom:4px">
              <span v-for="i in 5" :key="i" :style="{ color: i <= r.rating ? '#f59e0b' : '#e5e7eb', fontSize:'15px' }">★</span>
            </div>
            <p style="font-size:12px;font-weight:500;color:#374151">{{ r.reviewer_name || 'Anonymous' }}</p>
            <p style="font-size:11px;color:#9ca3af">{{ dayjs(r.created_at).format('MMM D, YYYY') }}</p>
            <n-tag v-if="r.is_verified_purchase" type="success" size="small" round style="margin-top:4px">Verified</n-tag>
          </div>
          <div style="flex:1;min-width:0">
            <p style="font-size:13px;color:#374151;line-height:1.6">{{ r.content || '(no text)' }}</p>
            <div v-if="r.media?.length" class="review-media-grid">
              <div v-for="m in r.media" :key="m.id" class="review-media-item">
                <n-image
                  v-if="m.media_type === 'image'"
                  :src="m.url"
                  fit="cover"
                  width="100%"
                  height="100%"
                  :preview-src-list="[m.url]"
                />
                <video
                  v-else
                  class="review-media-video"
                  :src="m.url"
                  controls
                  muted
                  playsinline
                  preload="metadata"
                ></video>
              </div>
            </div>
            <n-tag :type="r.status==='approved'?'success':r.status==='rejected'?'error':'warning'" size="small" round style="margin-top:6px">{{ r.status }}</n-tag>
          </div>
          <div v-if="r.status==='pending'" style="flex-shrink:0;display:flex;flex-direction:column;gap:6px">
            <n-button size="small" type="primary" :loading="moderating===r.id" @click="moderate(r.id,'approve')">Approve</n-button>
            <n-button size="small" type="error"   :loading="moderating===r.id" @click="moderate(r.id,'reject')">Reject</n-button>
          </div>
        </div>
      </div>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <n-pagination v-model:page="page" :item-count="total" :page-size="20" @update:page="load" />
      </div>
    </n-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { api, errMsg } from '@/composables/useApi'
import dayjs from 'dayjs'
const message = useMessage()
const reviews = ref<any[]>([])
const total = ref(0); const page = ref(1); const loading = ref(false)
const moderating = ref<number|null>(null); const statusFilter = ref('pending')
async function load() {
  loading.value = true
  try { const { data } = await api.reviews({ page: page.value, status: statusFilter.value || undefined }); reviews.value = data.items; total.value = data.total }
  catch { } finally { loading.value = false }
}
async function moderate(id: number, action: string) {
  moderating.value = id
  try { await api.moderateReview(id, { action }); message.success(action === 'approve' ? 'Approved' : 'Rejected'); load() }
  catch (e) { message.error(errMsg(e)) } finally { moderating.value = null }
}
onMounted(load)
</script>
<style scoped>
.page-header { display:flex;align-items:center;justify-content:space-between;margin-bottom:20px; }
.page-title { font-size:20px;font-weight:600;color:#18181b; }
.page-sub { font-size:13px;color:#9ca3af;margin-top:2px; }
.review-media-grid { display:flex;flex-wrap:wrap;gap:10px;margin-top:10px; }
.review-media-item { width:120px;height:85px;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;background:#f9fafb;display:flex; }
.review-media-item video { width:100%;height:100%;object-fit:cover;border:none; }
</style>
