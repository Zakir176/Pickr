<script setup>
import { ChevronLeft, Check, X, Heart, Maximize2, FileDigit } from 'lucide-vue-next';
import { ref, reactive } from 'vue';
import StatusBadge from './StatusBadge.vue';
import BestShotBadge from './BestShotBadge.vue';

defineProps({
  group: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['back', 'update-status', 'set-best', 'toggle-favorite']);

const handleSetStatus = (item, status) => {
  emit('update-status', item, status);
};

const handleSetBest = (item) => {
  emit('set-best', item);
};

// Smoother Swipe Gestures
const activeSwipeIndex = ref(null);
const swipeOffsets = reactive({}); // filename -> number

const touchState = {
  startX: 0,
  currentX: 0,
  isSwiping: false
};

const handleTouchStart = (e, filename) => {
  touchState.startX = e.touches[0].clientX;
  touchState.isSwiping = true;
  activeSwipeIndex.value = filename;
};

const handleTouchMove = (e, filename) => {
  if (!touchState.isSwiping || activeSwipeIndex.value !== filename) return;
  touchState.currentX = e.touches[0].clientX;
  const deltaX = touchState.currentX - touchState.startX;
  
  if (Math.abs(deltaX) > 100) {
    swipeOffsets[filename] = deltaX > 0 ? 100 + (deltaX - 100) * 0.2 : -100 + (deltaX + 100) * 0.2;
  } else {
    swipeOffsets[filename] = deltaX;
  }
};

const handleTouchEnd = (e, item) => {
  if (!touchState.isSwiping) return;
  
  const finalDeltaX = touchState.currentX - touchState.startX;
  const SWIPE_THRESHOLD = 80;

  if (finalDeltaX > SWIPE_THRESHOLD) {
    handleSetStatus(item, 'Keep');
  } else if (finalDeltaX < -SWIPE_THRESHOLD) {
    handleSetStatus(item, 'Delete');
  }

  swipeOffsets[item.filename] = 0;
  touchState.isSwiping = false;
  activeSwipeIndex.value = null;
};
</script>

<template>
  <div class="group-detail">
    <!-- Header -->
    <header class="top-bar glass-panel">
      <button
        class="icon-btn"
        @click="$emit('back')"
      >
        <ChevronLeft :size="24" />
      </button>
      <div class="header-title">
        <h1>Review Group</h1>
        <p class="sub-text">
          {{ group.items.length }} items
        </p>
      </div>
      <button
        class="done-btn"
        @click="$emit('back')"
      >
        Next
      </button>
    </header>

    <div class="scroll-content">
      <transition-group
        name="slide-up"
        appear
      >
        <div
          v-for="(item, index) in group.items"
          :key="item.filename"
          class="item-card"
          :style="{ transitionDelay: `${index * 0.1}s` }"
        >
          <div class="image-container">
            <div 
              class="photo-inner"
              :style="{ transform: `translateX(${swipeOffsets[item.filename] || 0}px)` }"
              @touchstart="handleTouchStart($event, item.filename)"
              @touchmove="handleTouchMove($event, item.filename)"
              @touchend="handleTouchEnd($event, item)"
            >
              <img
                :src="item.blobUrl"
                class="photo-img"
                :alt="item.filename"
                loading="lazy"
              >
              
              <!-- Overlays -->
              <div class="badge-row top">
                <StatusBadge :status="item.recommendation" />
                <BestShotBadge 
                  :is-best="item.isBest" 
                  @toggle="handleSetBest(item)" 
                />
              </div>
            </div>
          </div>

          <div class="info-row">
            <div class="metrics">
              <span class="filename">{{ item.filename }}</span>
              <div class="pills">
                <span class="pill">Blur: {{ Math.round(item.score_components.blur * 100) }}%</span>
                <span class="pill">Exp: {{ Math.round(item.score_components.exposure * 100) }}%</span>
                <span v-if="item.metadata?.size" class="pill secondary">
                  <FileDigit :size="10" /> {{ item.metadata.size }}
                </span>
              </div>
            </div>
            
            <div class="actions">
              <button 
                class="action-btn favorite" 
                :class="{ active: item.isFavorite }"
                aria-label="Favorite Photo"
                @click="$emit('toggle-favorite', item)"
              >
                <Heart :size="20" :fill="item.isFavorite ? '#EF4444' : 'none'" :color="item.isFavorite ? '#EF4444' : 'currentColor'" />
              </button>
              <button 
                class="action-btn keep" 
                :class="{ active: item.recommendation === 'Keep' }"
                aria-label="Keep Photo"
                @click="handleSetStatus(item, 'Keep')"
              >
                <Check :size="20" />
              </button>
              <button 
                class="action-btn delete" 
                :class="{ active: item.recommendation === 'Delete' }"
                aria-label="Delete Photo"
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

.photo-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.1s ease-out;
}

.photo-inner[style*="translateX(0px)"] {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.pill.secondary {
  background: rgba(59, 130, 246, 0.05);
  color: var(--primary-blue);
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
