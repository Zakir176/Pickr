<script setup>
import { ChevronLeft, Check, X, Heart, Maximize2, FileDigit, Columns, Bookmark } from 'lucide-vue-next';
import { ref, reactive, computed } from 'vue';
import StatusBadge from './StatusBadge.vue';
import BestShotBadge from './BestShotBadge.vue';

const props = defineProps({
  group: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['back', 'update-status', 'set-best', 'toggle-favorite']);

// Comparison Logic
const selectedForComparison = ref([]);
const isComparisonMode = ref(false);

const toggleSelection = (item) => {
  const index = selectedForComparison.value.findIndex(i => i.filename === item.filename);
  if (index === -1) {
    if (selectedForComparison.value.length >= 2) {
      selectedForComparison.value.shift();
    }
    selectedForComparison.value.push(item);
  } else {
    selectedForComparison.value.splice(index, 1);
  }
};

const isSelected = (filename) => {
  return selectedForComparison.value.some(i => i.filename === filename);
};

const canCompare = computed(() => selectedForComparison.value.length === 2);

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
      <div class="header-actions">
        <button
          v-if="canCompare"
          class="compare-btn-top"
          @click="isComparisonMode = true"
        >
          <Columns :size="18" />
          <span>Compare 2</span>
        </button>
        <button
          class="done-btn"
          @click="$emit('back')"
        >
          Next
        </button>
      </div>
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
                <div class="top-right-badges">
                  <button 
                    class="compare-toggle"
                    :class="{ selected: isSelected(item.filename) }"
                    @click.stop="toggleSelection(item)"
                    title="Select for comparison"
                  >
                    <Columns :size="14" />
                  </button>
                  <BestShotBadge 
                  :is-best="item.isBest" 
                  @toggle="handleSetBest(item)" 
                />
              </div>

              <!-- Face Bounding Boxes -->
              <div 
                v-for="(face, idx) in item.faces" 
                :key="idx"
                class="face-box"
                :style="{
                  left: (face.x / item.dimensions.width * 100) + '%',
                  top: (face.y / item.dimensions.height * 100) + '%',
                  width: (face.w / item.dimensions.width * 100) + '%',
                  height: (face.h / item.dimensions.height * 100) + '%'
                }"
              >
                <div class="face-tag">Face detected</div>
              </div>
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
                class="action-btn hold" 
                :class="{ active: item.recommendation === 'Hold' }"
                aria-label="Hold Photo"
                @click="handleSetStatus(item, 'Hold')"
              >
                <Bookmark :size="20" />
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

    <!-- Comparison Overlay -->
    <transition name="fade">
      <div v-if="isComparisonMode" class="comparison-overlay">
        <header class="top-bar glass-panel overlay-header">
          <button class="icon-btn" @click="isComparisonMode = false">
            <X :size="24" />
          </button>
          <div class="header-title">
            <h1>Compare Photos</h1>
          </div>
          <div class="header-actions">
            <p class="sub-text">Pinch to zoom</p>
          </div>
        </header>

        <div class="comparison-grid">
          <div 
            v-for="item in selectedForComparison" 
            :key="item.filename" 
            class="compare-item"
          >
            <div class="compare-photo-container">
              <img :src="item.blobUrl" :alt="item.filename" class="compare-img">
              <div class="compare-info">
                <span class="filename">{{ item.filename }}</span>
                <div class="actions mini">
                  <button 
                    class="action-btn mini keep" 
                    :class="{ active: item.recommendation === 'Keep' }"
                    @click="handleSetStatus(item, 'Keep')"
                  >
                    <Check :size="16" />
                  </button>
                  <button 
                    class="action-btn mini delete" 
                    :class="{ active: item.recommendation === 'Delete' }"
                    @click="handleSetStatus(item, 'Delete')"
                  >
                    <X :size="16" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.compare-btn-top {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-blue);
  padding: 6px 12px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 700;
  transition: all 0.2s ease;
}

.compare-btn-top:active {
  transform: scale(0.95);
  background: rgba(59, 130, 246, 0.2);
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

.face-box {
  position: absolute;
  border: 2px solid #3B82F6;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  pointer-events: none;
  z-index: 5;
  transition: opacity 0.3s ease;
  opacity: 0.2; /* Subtle by default */
}

.image-container:hover .face-box {
  opacity: 0.8; /* Highlight on hover */
}

.face-tag {
  position: absolute;
  bottom: 100%;
  left: 0;
  background: #3B82F6;
  color: white;
  font-size: 8px;
  font-weight: 800;
  padding: 2px 4px;
  border-radius: 2px 2px 0 0;
  text-transform: uppercase;
  white-space: nowrap;
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

.top-right-badges {
  display: flex;
  gap: 8px;
  align-items: center;
}

.compare-toggle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(8px);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.2s ease;
}

.compare-toggle.selected {
  background: var(--primary-blue);
  color: white;
  transform: scale(1.1);
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

.action-btn.hold.active {
  background: #DBEAFE;
  color: #2563EB;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.action-btn.delete.active {
  background: #FEE2E2;
  color: #DC2626;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
}

/* Comparison Overlay Styles */
.comparison-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.overlay-header {
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.comparison-grid {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: #f0f0f0;
  overflow: hidden;
}

.compare-item {
  flex: 1;
  background: white;
  position: relative;
  overflow: hidden;
}

.compare-photo-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.compare-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.compare-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compare-info .filename {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions.mini {
  gap: 8px;
}

.action-btn.mini {
  width: 36px;
  height: 36px;
  border-radius: 10px;
}

@media (min-width: 768px) {
  .comparison-grid {
    flex-direction: row;
  }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
