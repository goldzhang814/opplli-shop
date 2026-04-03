/**
 * Channel tracking plugin
 * - Reads ?ref= from URL on every page load
 * - Saves to sessionStorage (survives navigation, cleared on tab close)
 * - Fires a visit event to the backend
 * - On checkout success, fires an order event
 */
export default defineNuxtPlugin(() => {
  const route  = useRoute()
  const config = useRuntimeConfig()
  const BASE   = config.public.apiBase

  // Track visit on each navigation
  const trackVisit = (ref: string) => {
    fetch(`${BASE}/api/v1/track?ref=${encodeURIComponent(ref)}&event=visit`, {
      mode: 'no-cors',
    }).catch(() => {})
  }

  // Read ref from URL → save to sessionStorage
  const initTracking = () => {
    const ref = route.query.ref as string
    if (ref) {
      sessionStorage.setItem('channel_ref', ref)
      trackVisit(ref)
    }
  }

  // Run on mount
  if (typeof window !== 'undefined') {
    initTracking()

    // Also watch route changes (for SPA navigation)
    watch(() => route.query.ref, (newRef) => {
      if (newRef) {
        sessionStorage.setItem('channel_ref', newRef as string)
        trackVisit(newRef as string)
      }
    })
  }

  // Expose getRef for checkout to use
  return {
    provide: {
      getChannelRef: () => sessionStorage.getItem('channel_ref') || undefined,
    },
  }
})