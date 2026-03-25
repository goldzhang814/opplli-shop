/**
 * Typed API composable
 * Uses $fetch (Nuxt's ofetch) — SSR-safe, auto-forwards cookies.
 * Guest token is sent via X-Guest-Token header.
 */
import type { FetchOptions } from 'ofetch'
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

export function useApi() {
  const config  = useRuntimeConfig()
  const base    = config.public.apiBase

  const getHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {}
    const auth  = useAuthStore()
    const cart  = useCartStore()
    if (auth.token)       headers['Authorization']  = `Bearer ${auth.token}`
    if (cart.guestToken)  headers['X-Guest-Token']  = cart.guestToken
    return headers
  }

  const api = async <T = unknown>(
    endpoint: string,
    opts?: FetchOptions,
  ): Promise<T> => {
    return $fetch<T>(`${base}/api/v1${endpoint}`, {
      ...opts,
      headers: { ...getHeaders(), ...(opts?.headers ?? {}) },
      onResponseError: ({ response }) => {
        if (response.status === 401) {
          useAuthStore().logout()
        }
      },
    })
  }

  return {
    // Auth
    register:        (body: object)            => api('/auth/register', { method: 'POST', body }),
    login:           (body: object)            => api('/auth/login',    { method: 'POST', body }),
    me:              ()                        => api('/auth/me'),
    updateMe:        (body: object)            => api('/auth/me',       { method: 'PUT',  body }),
    guestCheckout:   (body: object)            => api('/auth/guest',    { method: 'POST', body }),
    forgotPassword:  (body: object)            => api('/auth/forgot-password', { method: 'POST', body }),
    resetPassword:   (body: object)            => api('/auth/reset-password',  { method: 'POST', body }),

    // Products
    listProducts:    (q?: object)              => api('/products',       { query: q }),
    getProduct:      (slug: string)            => api(`/products/${slug}`),
    getCategories:   ()                        => api('/categories'),

    // Reviews
    listReviews:     (productId: number, q?: object) =>
      api(`/products/${productId}/reviews`, { query: q }),
    submitReview:    (productId: number, body: FormData) =>
      api(`/products/${productId}/reviews`, { method: 'POST', body }),

    // Wishlist
    getWishlist:     ()                        => api('/wishlist'),
    getWishlistIds:  ()                        => api('/wishlist/ids'),
    toggleWishlist:  (productId: number)       => api(`/wishlist/${productId}`, { method: 'POST' }),

    // Cart
    getCart:         ()                        => api('/cart'),
    addToCart:       (body: object)            => api('/cart/items',     { method: 'POST', body }),
    updateCartItem:  (skuId: number, quantity: number) =>
      api(`/cart/items/${skuId}`, { method: 'PUT', body: { quantity } }),
    removeCartItem:  (skuId: number)           => api(`/cart/items/${skuId}`, { method: 'DELETE' }),
    clearCart:       ()                        => api('/cart',            { method: 'DELETE' }),
    mergeCart:       (guestToken: string)      => api('/cart/merge',      { method: 'POST', body: { guest_token: guestToken } }),

    // Checkout
    validateCoupon:  (body: object)            => api('/checkout/coupon/validate', { method: 'POST', body }),
    shippingEstimate:(body: object)            => api('/checkout/shipping-estimate', { method: 'POST', body }),
    checkoutPreview: (body: object)            => api('/checkout/preview',          { method: 'POST', body }),
    placeOrder:      (body: object)            => api('/checkout/place-order',      { method: 'POST', body }),

    // Shipping regions
    shippableCountries: ()                     => api('/shipping-regions/countries'),
    shippableStates:    (cc: string)           => api(`/shipping-regions/states/${cc}`),

    // Payment
    initStripe:      (orderId: number)         => api('/payments/stripe/intent',     { method: 'POST', body: { order_id: orderId } }),
    initPayPal:      (orderId: number)         => api('/payments/paypal/order',     { method: 'POST', body: { order_id: orderId } }),
    initAirwallex:   (orderId: number)         => api('/payments/airwallex/intent',  { method: 'POST', body: { order_id: orderId } }),

    // Addresses
    listAddresses:   ()                            => api('/auth/addresses'),
    createAddress:   (body: object)                => api('/auth/addresses',               { method: 'POST',   body }),
    updateAddress:   (id: number, body: object)    => api(`/auth/addresses/${id}`,          { method: 'PUT',    body }),
    deleteAddress:   (id: number)                  => api(`/auth/addresses/${id}`,          { method: 'DELETE' }),
    setDefaultAddr:  (id: number)                  => api(`/auth/addresses/${id}/set-default`, { method: 'POST' }),

    // Orders
    listOrders:      (page?: number)           => api('/orders', { query: { page } }),
    getOrder:        (id: number)              => api(`/orders/${id}`),
    cancelOrder:     (id: number)              => api(`/orders/${id}/cancel`,        { method: 'POST' }),
    requestRefund:   (id: number)              => api(`/orders/${id}/refund-request`,{ method: 'POST' }),

    // Content
    listBlog:        (q?: object)              => api('/blog',           { query: q }),
    getBlog:         (slug: string)            => api(`/blog/${slug}`),
    getBlogCategories: ()                      => api('/blog/categories'),
    getFaq:          (q?: object)              => api('/faq',           { query: q }),
    getFaqCategories:(q?: object)              => api('/faq/categories', { query: q }),
    getCmsPage:      (type: string, lang = 'en') => api(`/pages/${type}`, { query: { lang } }),
    getBanners:      ()                        => api('/banners'),
    getI18n:         (lang: string)            => api(`/i18n/${lang}`),
    getCookieConfig: (lang = 'en')             => api(`/cookie-consent`, { query: { lang } }),

    // Newsletter
    subscribe:       (body: object)            => api('/newsletter/subscribe', { method: 'POST', body }),
    unsubscribe:     (token: string)           => api(`/newsletter/unsubscribe`, { query: { token } }),

    // Tracking
    track:           (ref: string, event = 'visit') =>
      $fetch(`${base}/api/v1/track`, { query: { ref, event } }).catch(() => {}),
  }
}
