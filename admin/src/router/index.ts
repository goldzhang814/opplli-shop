import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/components/layout/AppShell.vue'),
    children: [
      { path: '',         component: () => import('@/views/dashboard/Dashboard.vue') },
      { path: 'orders',   component: () => import('@/views/orders/Orders.vue') },
      { path: 'orders/:id', component: () => import('@/views/orders/OrderDetail.vue') },
      { path: 'products', component: () => import('@/views/products/Products.vue') },
      { path: 'products/new',    component: () => import('@/views/products/ProductForm.vue') },
      { path: 'products/:id/edit', component: () => import('@/views/products/ProductForm.vue') },
      { path: 'categories', component: () => import('@/views/products/Categories.vue') },
      { path: 'reviews',  component: () => import('@/views/products/Reviews.vue') },
      { path: 'inventory',component: () => import('@/views/products/Inventory.vue') },
      { path: 'users',    component: () => import('@/views/users/Users.vue') },
      { path: 'coupons',  component: () => import('@/views/coupons/Coupons.vue') },
      { path: 'marketing',component: () => import('@/views/marketing/Marketing.vue') },
      { path: 'content',  component: () => import('@/views/content/Content.vue') },
      { path: 'shipping', component: () => import('@/views/shipping/Shipping.vue') },
      { path: 'settings', component: () => import('@/views/settings/Settings.vue') },
      { path: 'admins',   component: () => import('@/views/admins/Admins.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Restore admin profile after page refresh (token exists but admin obj is null)
  if (auth.isLoggedIn && !auth.admin) {
    try {
      const { api } = await import('@/composables/useApi')
      const res = await api.me()
      auth.setAdmin(res.data)
    } catch {
      // Token invalid/expired — force re-login
      auth.logout()
      if (!to.meta.public) return '/login'
    }
  }

  if (!to.meta.public && !auth.isLoggedIn) {
    return '/login'
  }
  if (to.path === '/login' && auth.isLoggedIn) {
    return '/'
  }
})

export default router
