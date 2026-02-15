<script setup>
import { ChevronLeft, Check, X, Star } from 'lucide-vue-next';
import { computed } from 'vue';
import StatusBadge from './StatusBadge.vue';

const props = defineProps({
  group: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['back', 'toggle-keep', 'set-best']);

const handleToggleKeep = (item) => {
  emit('toggle-keep', item);
};

const handleSetBest = (item) => {
  emit('set-best', item);
};

// Simple quality label helper
const getQualityLabel = (score) => {
  if (score > 0.8) return 'High';
  if (score > 0.5) return 'Medium';
  return 'Low';
};
</script>

<template>
  <div class="group-detail">
    <!-- Header -->
    <header class="top-bar">
      <button class="icon-btn" @click="$emit('back')">
        <ChevronLeft :size="24" />
      </button>
      <div class="header-title">
        <h1>Review Group</h1>
        <p class="sub-text">{{ group.items.length }} items</p>
      </div>
      <button class="done-btn" @click="$emit('back')">Next Group</button>
    </header>

    <div class="scroll-content">
      <div v-for="(item, index) in group.items" :key="index" class="item-card">
        <div class="image-container">
          <img :src="item.blobUrl" class="photo-img" :alt="item.filename" />
          
          <!-- Overlays -->
          <div class="badge-row top">
             <StatusBadge :status="item.recommendation" />
             <button 
                class="best-shot-indicator" 
                :class="{ active: item.isBest }"
                @click="handleSetBest(item)"
             >
               <Star 
                 :size="16" 
                 :fill="item.isBest ? '#FBBF24' : 'none'" 
                 :color="item.isBest ? '#FBBF24' : 'white'" 
                 :class="{ 'glow-star': item.isBest }"
               />
               <span v-if="item.isBest">Best Shot</span>
             </button>
          </div>
        </div>

        <div class="info-row">
          <div class="metrics">
            <span class="filename">{{ item.filename }}</span>
            <div class="pills">
               <span class="pill">Blur: {{ Math.round(item.score_components.blur * 100) }}%</span>
               <span class="pill">Exp: {{ Math.round(item.score_components.exposure * 100) }}%</span>
            </div>
          </div>
          
          <div class="actions">
            <button 
              class="action-btn keep" 
              :class="{ active: item.recommendation === 'Keep' }"
              @click="handleToggleKeep(item)"
            >
              <Check :size="20" />
            </button>
            <button 
              class="action-btn delete" 
              :class="{ active: item.recommendation === 'Delete' }"
              @click="handleToggleKeep(item)"
            >
              <X :size="20" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.group-detail {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--white);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #E5E7EB;
  background: var(--white);
}

.header-title {
  text-align: center;
}

h1 {
  font-size: 18px;
  font-weight: 700;
}

.sub-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.done-btn {
  color: var(--primary-blue);
  font-weight: 700;
  font-size: 15px;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.item-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 20px;
  overflow: hidden;
  background-color: #F3F4F6;
  box-shadow: var(--shadow-md);
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge-row.top {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.best-shot-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  padding: 6px 12px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.best-shot-indicator.active {
  background: rgba(251, 191, 36, 0.25);
  border-color: #FBBF24;
  color: #FBBF24;
  box-shadow: 0 0 15px rgba(251, 191, 36, 0.3);
}

.glow-star {
  filter: drop-shadow(0 0 4px #FBBF24);
  animation: star-pulse 2s infinite ease-in-out;
}

@keyframes star-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filename {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.pills {
  display: flex;
  gap: 6px;
}

.pill {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
  background: #F3F4F6;
  padding: 2px 8px;
  border-radius: 6px;
  text-transform: uppercase;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.action-btn.keep.active {
  background: #DCFCE7;
  color: #16A34A;
}

.action-btn.delete.active {
  background: #FEE2E2;
  color: #DC2626;
}
</style>
