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

const emit = defineEmits(['back', 'update-status', 'set-best']);

const handleSetStatus = (item, status) => {
  emit('update-status', item, status);
};

const handleSetBest = (item) => {
  emit('set-best', item);
};
</script>

<template>
  <div class="group-detail">
    <!-- Header -->
    <header class="top-bar glass-panel">
      <button class="icon-btn" @click="$emit('back')">
        <ChevronLeft :size="24" />
      </button>
      <div class="header-title">
        <h1>Review Group</h1>
        <p class="sub-text">{{ group.items.length }} items</p>
      </div>
      <button class="done-btn" @click="$emit('back')">Next</button>
    </header>

    <div class="scroll-content">
      <transition-group name="slide-up" appear>
        <div v-for="(item, index) in group.items" :key="item.filename" class="item-card" :style="{ transitionDelay: `${index * 0.1}s` }">
          <div class="image-container">
            <img :src="item.blobUrl" class="photo-img" :alt="item.filename" loading="lazy" />
            
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
                @click="handleSetStatus(item, 'Keep')"
              >
                <Check :size="20" />
              </button>
              <button 
                class="action-btn delete" 
                :class="{ active: item.recommendation === 'Delete' }"
                @click="handleSetStatus(item, 'Delete')"
              >
                <X :size="20" />
              </button>
            </div>
          </div>
        </div>
      </transition-group>
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
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
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
  font-weight: 800;
  font-size: 15px;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@media (min-width: 768px) {
  .scroll-content {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    align-content: start;
    gap: 24px;
  }
}

@media (min-width: 1024px) {
  .scroll-content {
    grid-template-columns: repeat(3, 1fr);
  }
}

.item-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 24px;
  overflow: hidden;
  background-color: #F3F4F6;
  box-shadow: var(--shadow);
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge-row.top {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.best-shot-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  padding: 8px 16px;
  border-radius: 100px;
  color: white;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.best-shot-indicator.active {
  background: rgba(251, 191, 36, 0.3);
  border-color: #FBBF24;
  color: #FBBF24;
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.4);
  transform: scale(1.05);
}

.glow-star {
  filter: drop-shadow(0 0 8px #FBBF24);
  animation: star-pulse 2s infinite ease-in-out;
}

@keyframes star-pulse {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 4px #FBBF24); }
  50% { transform: scale(1.2); filter: drop-shadow(0 0 12px #FBBF24); }
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filename {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.pills {
  display: flex;
  gap: 8px;
}

.pill {
  font-size: 10px;
  font-weight: 800;
  color: var(--text-secondary);
  background: #F3F4F6;
  padding: 4px 10px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.action-btn.keep.active {
  background: #DCFCE7;
  color: #16A34A;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);
}

.action-btn.delete.active {
  background: #FEE2E2;
  color: #DC2626;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
}
</style>
