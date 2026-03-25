<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <n-button quaternary @click="$router.back()">
        <template #icon><n-icon :component="ArrowBackOutline"/></template>
      </n-button>
      <h2 class="page-title">Order {{ order?.order_no }}</h2>
      <n-tag v-if="order" :type="statusColor[order.status]||'default'" round>{{ order.status.replace(/_/g,' ') }}</n-tag>
    </div>

    <div v-if="loading" style="text-align:center;padding:60px"><n-spin/></div>
    <div v-else-if="order">
      <n-grid :cols="2" :x-gap="16" :y-gap="16" responsive="screen" :item-responsive="true">
        <!-- Items -->
        <n-gi span="2">
          <n-card title="Order Items" :bordered="false" style="border-radius:14px">
            <div v-for="item in order.items" :key="item.id"
              style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #f3f4f6">
              <div style="width:40px;height:40px;border-radius:8px;background:#f3f4f6;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:18px;overflow:hidden">
                <img v-if="item.product_image" :src="item.product_image" style="width:100%;height:100%;object-fit:cover"/>
                <span v-else>🌿</span>
              </div>
              <div style="flex:1">
                <p style="font-size:13px;font-weight:500">{{ item.product_name }}</p>
                <p v-if="item.variant_attrs" style="font-size:11px;color:#9ca3af">{{ Object.values(item.variant_attrs).join(' / ') }}</p>
              </div>
              <p style="font-size:13px;color:#6b7280">×{{ item.quantity }}</p>
              <p style="font-weight:600;font-size:13px">${{ item.subtotal.toFixed(2) }}</p>
            </div>
            <!-- Totals -->
            <div style="margin-top:16px;border-top:1px solid #f3f4f6;padding-top:12px">
              <div v-for="row in totalsRows" :key="row.label" :style="`display:flex;justify-content:space-between;margin-bottom:6px;font-size:${row.bold?'14px':'13px'};font-weight:${row.bold?'700':'400'};color:${row.color||'#374151'}`">
                <span>{{ row.label }}</span><span>{{ row.value }}</span>
              </div>
            </div>
          </n-card>
        </n-gi>

        <!-- Shipping address -->
        <n-gi span="2 l:1">
          <n-card title="Shipping Address" :bordered="false" style="border-radius:14px">
            <div v-if="order.shipping_address" style="font-size:13px;color:#374151;line-height:1.8">
              <p style="font-weight:500">{{ order.shipping_address.full_name }}</p>
              <p>{{ order.shipping_address.address_line1 }}</p>
              <p v-if="order.shipping_address.address_line2">{{ order.shipping_address.address_line2 }}</p>
              <p>{{ order.shipping_address.city }}, {{ order.shipping_address.state_code || order.shipping_address.state_name }} {{ order.shipping_address.postal_code }}</p>
              <p>{{ order.shipping_address.country_code }}</p>
              <p v-if="order.shipping_address.phone" style="margin-top:4px;color:#6b7280">{{ order.shipping_address.phone }}</p>
            </div>
          </n-card>
        </n-gi>

        <!-- Payment + shipment -->
        <n-gi span="2 l:1">
          <n-card title="Payment & Shipment" :bordered="false" style="border-radius:14px">
            <div style="font-size:13px;line-height:2">
              <div style="display:flex;justify-content:space-between">
                <span style="color:#6b7280">Payment</span>
                <span style="text-transform:capitalize">{{ order.payment_method || '—' }}</span>
              </div>
              <div style="display:flex;justify-content:space-between">
                <span style="color:#6b7280">Pay Status</span>
                <n-tag :type="order.payment_status==='paid'?'success':'warning'" size="small" round>{{ order.payment_status }}</n-tag>
              </div>
              <template v-if="order.shipment">
                <n-divider style="margin:8px 0"/>
                <div style="display:flex;justify-content:space-between">
                  <span style="color:#6b7280">Carrier</span><span>{{ order.shipment.carrier_name }}</span>
                </div>
                <div style="display:flex;justify-content:space-between">
                  <span style="color:#6b7280">Tracking</span>
                  <a v-if="order.shipment.tracking_url" :href="order.shipment.tracking_url" target="_blank" style="color:#10b981;font-family:monospace;font-size:12px">{{ order.shipment.tracking_no }} ↗</a>
                  <code v-else style="font-size:12px">{{ order.shipment.tracking_no }}</code>
                </div>
              </template>
            </div>
          </n-card>
        </n-gi>

        <!-- Admin actions -->
        <n-gi span="2">
          <n-card title="Actions" :bordered="false" style="border-radius:14px">
            <n-space>
              <!-- Ship -->
              <n-button v-if="order.status==='pending_shipment'" type="primary" @click="showShipModal=true">
                Mark as Shipped
              </n-button>
              <!-- Refund -->
              <n-button v-if="['paid','completed','refund_requested'].includes(order.payment_status)" type="error" @click="showRefundModal=true">
                Process Refund
              </n-button>
              <!-- Admin note -->
              <n-button @click="showNoteModal=true">Add Admin Note</n-button>
            </n-space>
            <n-divider v-if="order.admin_note" />
            <p v-if="order.admin_note" style="font-size:13px;color:#6b7280;font-style:italic">Note: {{ order.admin_note }}</p>
          </n-card>
        </n-gi>
      </n-grid>
    </div>

    <!-- Ship modal -->
    <n-modal v-model:show="showShipModal" :mask-closable="false">
      <n-card style="width:420px;border-radius:14px" title="Mark as Shipped">
        <n-form :model="shipForm" label-placement="top" size="medium">
          <n-form-item label="Carrier ID *">
            <n-input-number v-model:value="shipForm.carrier_id" :min="1" style="width:100%"/>
          </n-form-item>
          <n-form-item label="Tracking Number *">
            <n-input v-model:value="shipForm.tracking_no" placeholder="1Z999AA10123456784"/>
          </n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showShipModal=false">Cancel</n-button>
          <n-button type="primary" :loading="acting" @click="doShip">Confirm Ship</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Refund modal -->
    <n-modal v-model:show="showRefundModal" :mask-closable="false">
      <n-card style="width:400px;border-radius:14px" title="Process Refund">
        <p style="font-size:13px;color:#6b7280;margin-bottom:16px">Leave amount empty for full refund of ${{ order?.total_amount?.toFixed(2) }}.</p>
        <n-form label-placement="top" size="medium">
          <n-form-item label="Refund Amount ($)">
            <n-input-number v-model:value="refundAmount" :min="0.01" :max="order?.total_amount" style="width:100%" placeholder="Full refund if empty"/>
          </n-form-item>
          <n-form-item label="Reason">
            <n-input v-model:value="refundReason" placeholder="Customer request…"/>
          </n-form-item>
        </n-form>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showRefundModal=false">Cancel</n-button>
          <n-button type="error" :loading="acting" @click="doRefund">Process Refund</n-button>
        </n-space>
      </n-card>
    </n-modal>

    <!-- Note modal -->
    <n-modal v-model:show="showNoteModal" :mask-closable="false">
      <n-card style="width:400px;border-radius:14px" title="Admin Note">
        <n-input v-model:value="adminNote" type="textarea" :rows="4" placeholder="Internal note…"/>
        <n-space justify="end" style="margin-top:12px">
          <n-button @click="showNoteModal=false">Cancel</n-button>
          <n-button type="primary" :loading="acting" @click="saveNote">Save Note</n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBackOutline } from '@vicons/ionicons5'
import { api, errMsg } from '@/composables/useApi'

const route   = useRoute()
const message = useMessage()
const loading = ref(false)
const order   = ref<any>(null)
const acting  = ref(false)

const showShipModal   = ref(false)
const showRefundModal = ref(false)
const showNoteModal   = ref(false)
const shipForm        = reactive({ carrier_id: 1, tracking_no: '' })
const refundAmount    = ref<number|null>(null)
const refundReason    = ref('')
const adminNote       = ref('')

const statusColor: Record<string,any> = {
  pending_payment:'warning', pending_shipment:'info',
  shipped:'success', completed:'success', cancelled:'default', refunded:'error'
}

async function load() {
  loading.value = true
  try { order.value = (await api.order(Number(route.params.id))).data }
  catch {} finally { loading.value = false }
}

const totalsRows = computed(() => {
  if (!order.value) return []
  const o = order.value
  const rows: any[] = [
    { label:'Subtotal',  value:`$${o.subtotal.toFixed(2)}` },
    { label:'Shipping',  value: o.shipping_fee===0 ? 'Free' : `$${o.shipping_fee.toFixed(2)}` },
    { label:'Tax',       value:`$${o.tax_amount.toFixed(2)}` },
  ]
  if (o.discount_amount > 0) rows.push({ label:'Discount', value:`-$${o.discount_amount.toFixed(2)}`, color:'#10b981' })
  rows.push({ label:'Total', value:`$${o.total_amount.toFixed(2)}`, bold: true })
  return rows
})

async function doShip() {
  acting.value = true
  try {
    await api.shipOrder(order.value.id, { carrier_id: shipForm.carrier_id, tracking_no: shipForm.tracking_no })
    message.success('Shipped!'); showShipModal.value = false; load()
  } catch (e) { message.error(errMsg(e)) }
  finally { acting.value = false }
}

async function doRefund() {
  acting.value = true
  try {
    await api.refundOrder(order.value.id, { amount: refundAmount.value || undefined, reason: refundReason.value || undefined })
    message.success('Refund initiated'); showRefundModal.value = false; load()
  } catch (e) { message.error(errMsg(e)) }
  finally { acting.value = false }
}

async function saveNote() {
  acting.value = true
  try {
    await api.updateOrder(order.value.id, { admin_note: adminNote.value })
    message.success('Note saved'); showNoteModal.value = false; load()
  } catch (e) { message.error(errMsg(e)) }
  finally { acting.value = false }
}

onMounted(() => { load(); })
</script>
<style scoped>
.page-title { font-size:20px; font-weight:600; color:#18181b; }
</style>
