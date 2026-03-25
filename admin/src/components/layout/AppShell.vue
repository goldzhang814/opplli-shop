<template>
  <n-layout has-sider style="height:100vh">
    <!-- Sidebar -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="224"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      style="background:#18181b"
    >
      <!-- Logo -->
      <div class="logo" :class="{ collapsed }">
        <div class="logo-icon">A</div>
        <span v-if="!collapsed" class="logo-text">Admin Panel</span>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        :indent="18"
        :theme-overrides="menuTheme"
        style="background:#18181b"
        @update:value="handleMenu"
      />

      <!-- Admin info -->
      <div v-if="!collapsed" class="admin-info">
        <n-avatar round size="small" :style="{ background: '#10b981', color: '#fff', flexShrink: 0 }">
          {{ initial }}
        </n-avatar>
        <div class="admin-meta">
          <p class="admin-name">{{ auth.admin?.full_name || auth.admin?.email }}</p>
          <p class="admin-role">{{ auth.admin?.role }}</p>
        </div>
        <n-button quaternary circle size="small" @click="logout" style="color:#71717a; flex-shrink:0">
          <template #icon><n-icon :component="LogOutOutline" /></template>
        </n-button>
      </div>
    </n-layout-sider>

    <!-- Main -->
    <n-layout>
      <!-- Topbar -->
      <n-layout-header bordered style="height:60px; padding:0 24px; display:flex; align-items:center; justify-content:space-between; background:#fff">
        <n-breadcrumb>
          <n-breadcrumb-item>Admin</n-breadcrumb-item>
          <n-breadcrumb-item>{{ currentPageName }}</n-breadcrumb-item>
        </n-breadcrumb>
        <div style="display:flex;align-items:center;gap:12px">
          <n-tag type="success" size="small">Online</n-tag>
          <a :href="storeUrl" target="_blank">
            <n-button size="small" quaternary>View Store ↗</n-button>
          </a>
        </div>
      </n-layout-header>

      <!-- Content -->
      <n-layout-content
        style="padding:24px; background:#f5f6fa; min-height:calc(100vh - 60px); overflow:auto"
      >
        <router-view v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { h, computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  BarChartOutline, CartOutline, CubeOutline, StarOutline,
  PeopleOutline, PricetagOutline, MegaphoneOutline, DocumentTextOutline,
  CarOutline, SettingsOutline, LogOutOutline, PersonOutline, ArchiveOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/composables/useApi'

const auth     = useAuthStore()
const router   = useRouter()
const route    = useRoute()
const collapsed= ref(false)

// Safety net: re-fetch admin profile if missing after page refresh
onMounted(async () => {
  if (auth.isLoggedIn && !auth.admin) {
    try {
      const res = await api.me()
      auth.setAdmin(res.data)
    } catch {
      auth.logout()
      router.push('/login')
    }
  }
})
const storeUrl = import.meta.env.VITE_STORE_URL || 'http://localhost:3000'

// Sidebar menu theme — light text on dark (#18181b) background
const menuTheme = {
  itemTextColor:               '#a1a1aa',   // normal
  itemTextColorHover:          '#f4f4f5',   // hover
  itemTextColorActive:         '#10b981',   // active
  itemTextColorActiveHover:    '#34d399',
  itemTextColorChildActive:    '#10b981',   // parent of active child
  itemTextColorChildActiveHover: '#34d399',
  itemColorActive:             'rgba(16,185,129,0.12)',
  itemColorActiveHover:        'rgba(16,185,129,0.18)',
  itemColorHover:              'rgba(255,255,255,0.06)',
  itemIconColor:               '#71717a',
  itemIconColorHover:          '#f4f4f5',
  itemIconColorActive:         '#10b981',
  itemIconColorChildActive:    '#10b981',
  itemIconColorCollapsed:      '#71717a',
  arrowColor:                  '#71717a',
  arrowColorHover:             '#d4d4d8',
  arrowColorActive:            '#10b981',
  arrowColorChildActive:       '#10b981',
  groupTextColor:              '#52525b',
  borderRadius:                '10px',
  itemHeight:                  '40px',
  collapsedIconSize:           '22px',
  dividerColor:                '#27272a',
}

const initial = computed(() =>
  (auth.admin?.full_name || auth.admin?.email || 'A')[0].toUpperCase()
)

const activeKey = computed(() => {
  const p = route.path
  if (p === '/')              return 'dashboard'
  if (p.startsWith('/orders'))return 'orders'
  if (p.startsWith('/products') || p.startsWith('/reviews') || p.startsWith('/inventory')) return 'products'
  return p.slice(1).split('/')[0]
})

const routeNames: Record<string, string> = {
  dashboard: 'Dashboard', orders: 'Orders', products: 'Products',
  reviews: 'Reviews', categories: 'Categories', inventory: 'Inventory', users: 'Users',
  coupons: 'Coupons', marketing: 'Marketing', content: 'Content',
  shipping: 'Shipping', settings: 'Settings', admins: 'Admins',
}
const currentPageName = computed(() => routeNames[activeKey.value] || 'Page')

function icon(C: any) {
  return () => h(NIcon, null, { default: () => h(C) })
}

const menuOptions = computed((): MenuOption[] => {
  const items: MenuOption[] = [
    { key: 'dashboard', label: 'Dashboard', icon: icon(BarChartOutline) },
  ]

  if (auth.can('orders'))
    items.push({ key: 'orders', label: 'Orders', icon: icon(CartOutline) })

  if (auth.can('products')) {
    items.push({ key: 'products-group', label: 'Products', icon: icon(CubeOutline), children: [
      { key: 'products',   label: 'All Products' },
      { key: 'categories', label: 'Categories' },
      { key: 'reviews',    label: 'Reviews' },
      { key: 'inventory',  label: 'Inventory' },
    ]})
  }

  if (auth.can('orders'))
    items.push({ key: 'users', label: 'Customers', icon: icon(PeopleOutline) })

  if (auth.can('coupons'))
    items.push({ key: 'coupons', label: 'Coupons', icon: icon(PricetagOutline) })

  if (auth.can('banners'))
    items.push({ key: 'marketing', label: 'Marketing', icon: icon(MegaphoneOutline) })

  if (auth.can('content'))
    items.push({ key: 'content', label: 'Content', icon: icon(DocumentTextOutline) })

  if (auth.can('shipping'))
    items.push({ key: 'shipping', label: 'Shipping & Tax', icon: icon(CarOutline) })

  if (auth.can('seo') || auth.can('settings'))
    items.push({ key: 'settings', label: 'Settings', icon: icon(SettingsOutline) })

  if (auth.can('admins'))
    items.push({ key: 'admins', label: 'Admins', icon: icon(PersonOutline) })

  return items
})

function handleMenu(key: string) {
  if (key.endsWith('-group')) return
  router.push(key === 'dashboard' ? '/' : `/${key}`)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.logo {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 16px; border-bottom: 1px solid #27272a;
  transition: padding 0.3s;
}
.logo.collapsed { padding: 18px 20px; justify-content: center; }
.logo-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: #10b981; color: #fff; font-weight: 700;
  font-size: 14px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-text { color: #f4f4f5; font-weight: 600; font-size: 15px; white-space: nowrap; }

.admin-info {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 12px 14px; border-top: 1px solid #27272a;
  display: flex; align-items: center; gap: 8px;
  background: #18181b;
}
.admin-meta { flex: 1; min-width: 0; }
.admin-name { color: #e4e4e7; font-size: 12px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.admin-role { color: #71717a; font-size: 11px; text-transform: capitalize; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
