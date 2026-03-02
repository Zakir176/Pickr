<script setup>
import { ChevronLeft, Sparkles, Loader2, Upload, Scissors } from 'lucide-vue-next';
import AppLogo from './AppLogo.vue';

defineProps({
  step: {
    type: String,
    default: 'analyzing'
  }
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
      <div class="spacer" />
    </header>

    <!-- Content -->
    <div class="content-center">
      <div class="pulse-circle">
        <div class="icon-wrapper">
          <Sparkles
            v-if="step === 'analyzing'"
            :size="48"
            color="#3B82F6"
            fill="#3B82F6"
          />
          <Upload 
            v-else-if="step === 'uploading'"
            :size="48"
            color="#3B82F6"
          />
          <Scissors
            v-else-if="step === 'resizing'"
            :size="48"
            color="#3B82F6"
          />
        </div>
      </div>

      <AppLogo />
      
      <div class="step-info mt-4">
        <div class="step-label">
          <Loader2 :size="16" class="animate-spin" />
          <span v-if="step === 'resizing'">Optimizing images...</span>
          <span v-else-if="step === 'uploading'">Sending to server...</span>
          <span v-else>Analyzing quality...</span>
        </div>
        <p class="sub-text">
          Finding duplicates and your best<br>shots to keep your gallery clean.
        </p>
      </div>
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
  width: 80px;
  height: 80px;
  background-color: #DBEAFE; /* Light blue circle */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
  z-index: 2;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}

.step-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.step-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: var(--primary-blue);
  background: rgba(59, 130, 246, 0.1);
  padding: 6px 16px;
  border-radius: 100px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.sub-text {
  font-size: 14px;
  color: var(--text-secondary);
}

.mt-4 {
  margin-top: 1rem;
}
</style>
