export default defineAppConfig({
  ui: {
    primary:    'emerald',
    gray:       'zinc',
    // Global component overrides
    button: {
      rounded:  'rounded-xl',
      default:  {
        size:   'md',
        color:  'primary',
        variant:'solid',
      },
    },
    input: {
      rounded: 'rounded-xl',
    },
    card: {
      rounded: 'rounded-2xl',
    },
    badge: {
      rounded: 'rounded-full',
    },
  },
})
