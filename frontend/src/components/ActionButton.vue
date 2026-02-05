<script setup>
import { ChartBar } from 'lucide-vue-next';

defineProps({
  label: {
    type: String,
    default: 'Analyze Photos'
  },
  icon: {
    type: Object,
    default: null
  }
});
</script>

<template>
  <button class="action-btn">
    <ChartBar :size="20" class="btn-icon" />
    <span>{{ label }}</span>
  </button>
</template>

<style scoped>
.action-btn {
  background-color: #60A5FA; /* Using a lighter blue as per the screenshot (looks like blue-400/500) or standard primary */
  background-color: var(--primary-blue); /* Let's stick to our variable */
  color: white;
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
  transition: transform 0.1s;
}

.action-btn:active {
  transform: scale(0.98);
}
</style>
