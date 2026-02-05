<script setup>
import { CloudUpload, Image as ImageIcon, Settings } from 'lucide-vue-next';
</script>

<template>
  <nav class="bottom-nav">
    <button class="nav-item active">
      <CloudUpload :size="24" />
      <span>UPLOAD</span>
    </button>
    <button class="nav-item">
      <ImageIcon :size="24" />
      <span>LIBRARY</span>
    </button>
    <button class="nav-item">
      <Settings :size="24" />
      <span>SETTINGS</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav {
  display: flex;
  justify-content: space-around;
  padding: 12px 16px 24px; /* Extra padding for bottom safe area */
  background-color: var(--white);
  border-top: 1px solid #E5E7EB;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #9CA3AF;
}

.nav-item span {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.nav-item.active {
  color: var(--primary-blue);
}
</style>
