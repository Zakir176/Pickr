<script setup>
import { CloudUpload, Image as ImageIcon, Settings } from 'lucide-vue-next';
</script>

<template>
  <nav class="bottom-nav glass-panel">
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
  padding: 12px 16px 32px;
  z-index: 100;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
  width: 100%;
  max-width: 480px; /* Keep nav compact even on desktop */
  margin: 0 auto;
  border-radius: 24px 24px 0 0;
}

@media (min-width: 768px) {
  .bottom-nav {
    padding-bottom: 20px;
    margin-bottom: 20px;
    border-radius: 100px;
    width: fit-content;
    gap: 40px;
    padding: 12px 40px;
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #9CA3AF;
  transition: var(--transition);
}

.nav-item span {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.8px;
}

.nav-item.active {
  color: var(--primary-blue);
  transform: translateY(-2px);
}
</style>
