<script setup>
import { ChevronLeft } from 'lucide-vue-next';
import AppLogo from './AppLogo.vue';
</script>

<template>
  <header class="top-bar glass-panel">
    <button class="icon-btn">
      <ChevronLeft :size="24" />
    </button>
    <AppLogo />
    <div class="spacer"></div>
  </header>
</template>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  z-index: 100;
}

h1 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.icon-btn {
  padding: 8px;
  margin-left: -8px;
  color: var(--text-primary);
  border-radius: 50%;
}

.icon-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.spacer {
  width: 24px;
}
</style>
