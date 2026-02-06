<script setup>
import { ChevronLeft } from 'lucide-vue-next';
</script>

<template>
  <header class="top-bar">
    <button class="icon-btn">
      <ChevronLeft :size="24" />
    </button>
    <h1>Upload Photos</h1>
    <div class="spacer"></div>
  </header>
</template>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: var(--bg-gray);
}

h1 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
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
  width: 24px; /* Balance the back arrow */
}
</style>
