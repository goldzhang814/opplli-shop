import { defineStore } from 'pinia'

interface CartItem {
  sku_id:        number
  sku_code:      string
  product_id:    number
  product_name:  string
  product_slug:  string
  variant_attrs: Record<string, string> | null
  quantity:      number
  unit_price:    number
  compare_price: number | null
  subtotal:      number
  stock:         number
  cover_image:   string | null
  free_shipping: boolean
}

interface CartState {
  items:       CartItem[]
  subtotal:    number
  guestToken:  string | null
  isOpen:      boolean
  loading:     boolean
}

export const useCartStore = defineStore('cart', {
  state: (): CartState => ({
    items:      [],
    subtotal:   0,
    guestToken: null,
    isOpen:     false,
    loading:    false,
  }),

  getters: {
    itemCount:    (s) => s.items.reduce((acc, i) => acc + i.quantity, 0),
    isEmpty:      (s) => s.items.length === 0,
    freeShipping: (s) => s.items.every((i) => i.free_shipping),
  },

  actions: {
    setCart(data: { items: CartItem[]; subtotal: number; guest_token?: string }) {
      this.items    = data.items
      this.subtotal = data.subtotal
      if (data.guest_token) this.guestToken = data.guest_token
    },

    clearCart() {
      this.items    = []
      this.subtotal = 0
    },

    openCart()  { this.isOpen = true },
    closeCart() { this.isOpen = false },
    toggleCart(){ this.isOpen = !this.isOpen },

    initGuestToken() {
      if (import.meta.client && !this.guestToken) {
        let token = localStorage.getItem('guest_token')
        if (!token) {
          token = crypto.randomUUID().replace(/-/g, '')
          localStorage.setItem('guest_token', token)
        }
        this.guestToken = token
      }
    },
  },

  persist: {
    storage: import.meta.client ? localStorage : undefined,
    paths:   ['guestToken'],
  },
})
