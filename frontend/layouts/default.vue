<template>
  <div class="flex flex-col min-h-screen" style="padding-top: var(--header-h)">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
    <CartDrawer />
  </div>
</template>
