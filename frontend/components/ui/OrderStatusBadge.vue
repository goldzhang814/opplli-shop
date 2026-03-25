<template>
  <span :class="badgeClass" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold">
    <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="dotClass" />
    {{ label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ status: string }>()
const { t } = useI18n()

const config: Record<string, { badge: string; dot: string }> = {
  pending_payment:  { badge: 'bg-amber-50  text-amber-700',  dot: 'bg-amber-500' },
  pending_shipment: { badge: 'bg-blue-50   text-blue-700',   dot: 'bg-blue-500' },
  shipped:          { badge: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' },
  completed:        { badge: 'bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' },
  cancelled:        { badge: 'bg-zinc-100  text-zinc-600',   dot: 'bg-zinc-400' },
  refunded:         { badge: 'bg-purple-50 text-purple-700', dot: 'bg-purple-500' },
  refund_requested: { badge: 'bg-amber-50  text-amber-700',  dot: 'bg-amber-500' },
}

const badgeClass = computed(() => config[props.status]?.badge ?? 'bg-zinc-100 text-zinc-600')
const dotClass   = computed(() => config[props.status]?.dot   ?? 'bg-zinc-400')
const label      = computed(() => t(`order.status.${props.status}`, props.status))
</script>
