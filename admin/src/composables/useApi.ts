import axios, { type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'

const BASE = import.meta.env.VITE_API_URL ?? ''

export const http = axios.create({
  baseURL: `${BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('admin_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

http.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export function errMsg(e: unknown): string {
  const err = e as AxiosError<{ detail: string | Array<{msg: string}> }>
  const d   = err.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d))      return d.map(x => x.msg).join(', ')
  return 'Something went wrong'
}

export const api = {
  // Auth
  login:           (data: object)                        => http.post('/admin/login', data),
  me:              ()                                    => http.get('/admin/me'),

  // Dashboard
  dashboard:       ()                                    => http.get('/admin/dashboard'),

  // Orders
  orders:          (p?: object)                          => http.get('/admin/orders', { params: p }),
  order:           (id: number)                          => http.get(`/admin/orders/${id}`),
  updateOrder:     (id: number, data: object)            => http.put(`/admin/orders/${id}`, data),
  shipOrder:       (id: number, data: object)            => http.post(`/admin/orders/${id}/ship`, data),
  refundOrder:     (id: number, data: object)            => http.post(`/admin/orders/${id}/refund`, data),
  webhooks:        (p?: object)                          => http.get('/admin/webhooks', { params: p }),

  // Users
  users:           (p?: object)                          => http.get('/admin/users', { params: p }),

  // Products
  products:        (p?: object)                          => http.get('/admin/products', { params: p }),
  product:         (id: number)                          => http.get(`/admin/products/${id}`),
  createProduct:   (data: object)                        => http.post('/admin/products', data),
  updateProduct:   (id: number, data: object)            => http.put(`/admin/products/${id}`, data),
  deleteProduct:   (id: number)                          => http.delete(`/admin/products/${id}`),
  publishProduct:  (id: number)                          => http.post(`/admin/products/${id}/publish`),
  unpublishProduct:(id: number)                          => http.post(`/admin/products/${id}/unpublish`),
  createSku:       (pid: number, data: object)           => http.post(`/admin/products/${pid}/skus`, data),
  updateSku:       (pid: number, sid: number, d: object) => http.put(`/admin/products/${pid}/skus/${sid}`, d),
  deleteSku:       (pid: number, sid: number)            => http.delete(`/admin/products/${pid}/skus/${sid}`),
  uploadImage:     (pid: number, form: FormData)         => http.post(`/admin/products/${pid}/images`, form, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteImage:     (pid: number, iid: number)            => http.delete(`/admin/products/${pid}/images/${iid}`),
  categories:      ()                                    => http.get('/admin/categories'),
  createCategory:  (data: object)                        => http.post('/admin/categories', data),
  updateCategory:  (id: number, data: object)            => http.put(`/admin/categories/${id}`, data),
  reviews:         (p?: object)                          => http.get('/admin/reviews', { params: p }),
  moderateReview:  (id: number, data: object)            => http.post(`/admin/reviews/${id}/moderate`, data),
  inventory:       (p?: object)                          => http.get('/admin/inventory/logs', { params: p }),
  adjustInventory: (skuId: number, data: object)         => http.post(`/admin/skus/${skuId}/inventory`, data),
  lowStock:        ()                                    => http.get('/admin/inventory/low-stock'),

  // Coupons
  coupons:         ()                                    => http.get('/admin/coupons'),
  createCoupon:    (data: object)                        => http.post('/admin/coupons', data),
  updateCoupon:    (id: number, data: object)            => http.put(`/admin/coupons/${id}`, data),
  deleteCoupon:    (id: number)                          => http.delete(`/admin/coupons/${id}`),

  // Marketing
  banners:         ()                                    => http.get('/admin/banners'),
  createBanner:    (data: object)                        => http.post('/admin/banners', data),
  updateBanner:    (id: number, data: object)            => http.put(`/admin/banners/${id}`, data),
  deleteBanner:    (id: number)                          => http.delete(`/admin/banners/${id}`),
  newsletter:      (p?: object)                          => http.get('/admin/newsletter', { params: p }),
  newsletterStats: ()                                    => http.get('/admin/newsletter/stats'),
  newsletterExport:()                                    => http.get('/admin/newsletter/export', { responseType: 'blob' }),
  deleteSubscriber:(id: number)                          => http.delete(`/admin/newsletter/${id}`),
  channels:        ()                                    => http.get('/admin/channels'),
  createChannel:   (data: object)                        => http.post('/admin/channels', data),
  updateChannel:   (id: number, data: object)            => http.put(`/admin/channels/${id}`, data),
  channelStats:    (id: number)                          => http.get(`/admin/channels/${id}/stats`),

  // Content
  blogPosts:       (p?: object)                          => http.get('/admin/blog', { params: p }),
  createPost:      (data: object)                        => http.post('/admin/blog', data),
  updatePost:      (id: number, data: object)            => http.put(`/admin/blog/${id}`, data),
  deletePost:      (id: number)                          => http.delete(`/admin/blog/${id}`),
  blogCategories:  ()                                    => http.get('/admin/blog/categories'),
  faqs:            (p?: object)                          => http.get('/admin/faq', { params: p }),
  createFaq:       (data: object)                        => http.post('/admin/faq', data),
  updateFaq:       (id: number, data: object)            => http.put(`/admin/faq/${id}`, data),
  deleteFaq:       (id: number)                          => http.delete(`/admin/faq/${id}`),
  cmsPages:        ()                                    => http.get('/admin/cms'),
  updateCmsPage:   (type: string, lang: string, d: object) => http.put(`/admin/cms/${type}/${lang}`, d),
  emailTemplates:  ()                                    => http.get('/admin/email-templates'),
  updateTemplate:  (type: string, lang: string, d: object) => http.put(`/admin/email-templates/${type}/${lang}`, d),
  sendTestEmail:   (data: object)                        => http.post('/admin/email-templates/test', data),
  cookieConfigs:   ()                                    => http.get('/admin/cookie-consent'),
  updateCookie:    (lang: string, data: object)          => http.put(`/admin/cookie-consent/${lang}`, data),

  // Settings
  settings:        ()                                    => http.get('/admin/settings'),
  updateSetting:   (key: string, value: string)          => http.put(`/admin/settings/${key}`, { value }),
  seo:             ()                                    => http.get('/admin/seo'),
  updateSeo:       (data: object)                        => http.put('/admin/seo', data),
  i18n:            (lang: string)                        => http.get(`/admin/i18n/${lang}`),
  updateI18n:      (lang: string, data: object)          => http.put(`/admin/i18n/${lang}`, data),

  // Shipping
  shippingZones:   ()                                    => http.get('/admin/shipping/zones'),
  createZone:      (data: object)                        => http.post('/admin/shipping/zones', data),
  updateZone:      (id: number, data: object)            => http.put(`/admin/shipping/zones/${id}`, data),
  shippingRegions: (p?: object)                          => http.get('/admin/shipping/regions', { params: p }),
  updateRegion:    (id: number, data: object)            => http.put(`/admin/shipping/regions/${id}`, data),
  shippingRules:   ()                                    => http.get('/admin/shipping/rules'),
  updateRule:      (id: number, data: object)            => http.put(`/admin/shipping/rules/${id}`, data),
  carriers:        ()                                    => http.get('/admin/carriers'),
  createCarrier:   (data: object)                        => http.post('/admin/carriers', data),
  updateCarrier:   (id: number, data: object)            => http.put(`/admin/carriers/${id}`, data),
  taxRules:        ()                                    => http.get('/admin/tax-rules'),
  createTax:       (data: object)                        => http.post('/admin/tax-rules', data),
  updateTax:       (id: number, data: object)            => http.put(`/admin/tax-rules/${id}`, data),
  deleteTax:       (id: number)                          => http.delete(`/admin/tax-rules/${id}`),

  // Admins
  admins:          ()                                    => http.get('/admin/admins'),
  createAdmin:     (data: object)                        => http.post('/admin/admins', data),
  updatePermissions:(id: number, data: object)           => http.put(`/admin/admins/${id}/permissions`, data),
  toggleAdminStatus:(id: number)                         => http.put(`/admin/admins/${id}/status`),
}
