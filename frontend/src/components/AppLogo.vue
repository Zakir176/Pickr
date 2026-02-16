<script setup>
import { Sparkles } from 'lucide-vue-next';
</script>

<template>
  <div class="logo-container">
    <div class="logo-mark glass-panel">
      <div class="shutter">
        <div class="blade" v-for="n in 6" :key="n"></div>
      </div>
      <Sparkles class="logo-icon" :size="24" />
    </div>
    <span class="logo-text">Pickr</span>
  </div>
</template>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-mark {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(135deg, var(--primary-blue), #60A5FA);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.logo-mark::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: translateX(-100%);
  animation: shine 3s infinite ease-in-out;
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  20%, 100% { transform: translateX(100%); }
}

.shutter {
  position: absolute;
  width: 300%;
  height: 300%;
  opacity: 0.1;
  animation: rotate-shutter 20s linear infinite;
}

.blade {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 2px;
  background: white;
  transform-origin: 0 50%;
}

.blade:nth-child(1) { transform: rotate(0deg); }
.blade:nth-child(2) { transform: rotate(60deg); }
.blade:nth-child(3) { transform: rotate(120deg); }
.blade:nth-child(4) { transform: rotate(180deg); }
.blade:nth-child(5) { transform: rotate(240deg); }
.blade:nth-child(6) { transform: rotate(300deg); }

@keyframes rotate-shutter {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.logo-icon {
  position: relative;
  z-index: 2;
  color: white;
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.5));
  animation: pulse-icon 2s infinite ease-in-out;
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.9; }
}

.logo-text {
  font-size: 22px;
  font-weight: 900;
  letter-spacing: -1px;
  background: linear-gradient(to bottom, var(--text-primary), #4B5563);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
