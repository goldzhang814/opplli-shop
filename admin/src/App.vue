<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="enUS" :date-locale="dateEnUS">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { enUS, dateEnUS } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor:        '#10b981',
    primaryColorHover:   '#059669',
    primaryColorPressed: '#047857',
    primaryColorSuppl:   '#34d399',
    borderRadius:        '10px',
    fontFamily:          "'Inter', system-ui, sans-serif",
  },
  Button: { borderRadius: '10px' },
  Card:   { borderRadius: '14px' },
  Input:  { borderRadius: '10px' },
  Select: { borderRadius: '10px' },
  DataTable: { thColor: '#f9fafb', tdColorHover: '#f0fdf4' },
}
</script>
