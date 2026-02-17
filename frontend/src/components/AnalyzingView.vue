<script setup>
import { ChevronLeft, Sparkles } from 'lucide-vue-next';
import AppLogo from './AppLogo.vue';

defineProps({
  // No props needed yet
});
</script>

<template>
  <div class="analyzing-view">
    <!-- Header -->
    <header class="top-bar">
      <button class="icon-btn">
        <ChevronLeft :size="24" />
      </button>
      <h1>Photo Curation</h1>
      <div class="spacer"></div>
    </header>

    <!-- Content -->
    <div class="content-center">
      <div class="pulse-circle">
        <div class="icon-wrapper">
          <Sparkles :size="48" color="#3B82F6" fill="#3B82F6" />
        </div>
      </div>

      <AppLogo />
      <p class="mt-4">Finding duplicates and your best<br>shots to keep your gallery clean.</p>
    </div>
  </div>
</template>

<style scoped>
.analyzing-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-gray);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: var(--bg-gray);
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
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

.spacer {
  width: 24px;
}

.content-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 32px;
  text-align: center;
  margin-top: -10%; /* Visual centering compensation */
}

/* Animation Container */
.pulse-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 4px solid #EFF6FF; /* Very light blue ring */
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  position: relative;
  animation: pulse-ring 2s infinite;
}

.icon-wrapper {
  width: 100px;
  height: 100px;
  background-color: #DBEAFE; /* Blue 100 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

p {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.5;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.2);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}
</style>
