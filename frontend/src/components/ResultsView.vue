<script setup>
import { ChevronLeft, Wand2, ChevronDown, Download, Check, X } from 'lucide-vue-next';
import StatusBadge from './StatusBadge.vue';
import BestShotBadge from './BestShotBadge.vue';
import { computed, ref, reactive } from 'vue';
import { getQualityLabel } from '../utils';

const props = defineProps({
  groups: {
    type: Array,
    default: () => []
  },
  flatResults: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['back', 'confirm', 'view-group', 'update-status', 'smart-clean', 'set-best']);

// Local state for collapsed groups
const collapsedGroups = ref({});

const toggleGroup = (groupTitle) => {
  collapsedGroups.value[groupTitle] = !collapsedGroups.value[groupTitle];
};

// Photo download
const downloadPhoto = (blobUrl, filename) => {
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = filename || 'downloaded_image.png';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Computing Stats
const totalPhotos = computed(() => props.flatResults.length);
const confirmedCount = computed(() => {
  return props.flatResults.filter(r => r.isConfirmed).length;
});


const deletionsCount = computed(() => {
  return props.flatResults.filter(r => r.recommendation === 'Delete').length;
});



// Quality labeling moved to utils.js

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
  
  // Resistance when swiping too far
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

  // Reset with transition
  swipeOffsets[item.filename] = 0;
  touchState.isSwiping = false;
  activeSwipeIndex.value = null;
};
</script>

<template>
  <div class="results-view">
    <!-- Header -->
    <header class="top-bar glass-panel">
      <button
        class="icon-btn"
        @click="$emit('back')"
      >
        <ChevronLeft :size="24" />
      </button>
      <h1>Curation Results</h1>
      <button
        class="smart-btn"
        aria-label="Smart Clean Bulk Action"
        title="Smart Clean"
        @click="$emit('smart-clean')"
      >
        <Wand2 :size="16" />
        <span>Smart Clean</span>
      </button>
    </header>

    <div class="scroll-content">
      <!-- Summary Cards -->
      <div class="stats-row">
        <div class="stat-card">
          <span class="label">PHOTOS ANALYZED</span>
          <span class="value">{{ totalPhotos }}</span>
        </div>
        <div class="stat-card">
          <span class="label">TO CLEAN UP</span>
          <span class="value red">{{ deletionsCount }}</span>
        </div>
      </div>

      <!-- Groups -->
      <div
        v-for="(group, idx) in groups"
        :key="idx"
        class="group-section"
      >
        <div
          class="group-header clickable"
          @click="toggleGroup(group.title)"
        >
          <h3>{{ group.title }}</h3>
          <div class="group-header-right">
            <span
              v-if="group.items.length > 1"
              class="sub-text"
            >Best match selected</span>
            <ChevronDown
              :class="{ 'rotate-180': collapsedGroups[group.title] }"
              :size="20"
              class="chevron-icon"
            />
          </div>
        </div>

        <transition name="fade">
          <div
            v-if="!collapsedGroups[group.title]"
            class="grid-responsive photo-grid-spacing"
          >
            <div 
              v-for="(item, i) in group.items"
              :key="i" 
              class="photo-card" 
              @click="$emit('view-group', group)"
            >
              <div 
                class="photo-inner"
                :style="{ transform: `translateX(${swipeOffsets[item.filename] || 0}px)` }"
                @touchstart="handleTouchStart($event, item.filename)"
                @touchmove="handleTouchMove($event, item.filename)"
                @touchend="handleTouchEnd($event, item)"
              >
                <img 
                  v-if="item.blobUrl" 
                  :src="item.blobUrl" 
                  class="photo-img" 
                  alt="Analyzed photo" 
                  loading="lazy"
                >
                <div
                  v-else
                  class="img-placeholder"
                >
                  <span class="filename">{{ item.filename }}</span>
                </div>
                
                <!-- Download Button -->
                <button
                  v-if="item.blobUrl"
                  class="download-btn"
                  @click.stop="downloadPhoto(item.blobUrl, item.filename)"
                >
                  <Download
                    :size="16"
                    color="white"
                  />
                </button>

                <div class="badge-overlay">
                  <StatusBadge
                    :status="item.error ? 'Error' : item.recommendation"
                    :error-message="item.error"
                  />
                  <BestShotBadge 
                    v-if="item.isBest" 
                    :is-best="true" 
                    style="margin-top: 8px;" 
                    @toggle="handleSetBest(item)"
                  />
                </div>

                <!-- Manual Toggle Controls -->
                <div
                  class="control-overlay"
                  @click.stop
                >
                  <button 
                    class="ctrl-btn keep" 
                    :class="{ active: item.recommendation === 'Keep' }"
                    aria-label="Keep Photo"
                    @click="handleSetStatus(item, 'Keep')"
                  >
                    <Check :size="14" />
                  </button>
                  <button 
                    class="ctrl-btn delete" 
                    :class="{ active: item.recommendation === 'Delete' }"
                    aria-label="Delete Photo"
                    @click="handleSetStatus(item, 'Delete')"
                  >
                    <X :size="14" />
                  </button>
                </div>
                
                <!-- Quality Label -->
                <div class="quality-overlay">
                  <StatusBadge
                    :status="getQualityLabel(item.final_score)"
                    type="label"
                  />
                </div>
              </div>
              
              <!-- Swipe Background Indicators -->
              <div
                class="swipe-bg swipe-keep"
                :style="{ opacity: (swipeOffsets[item.filename] || 0) / 100 }"
              >
                <Check
                  :size="32"
                  color="white"
                />
              </div>
              <div
                class="swipe-bg swipe-delete"
                :style="{ opacity: -(swipeOffsets[item.filename] || 0) / 100 }"
              >
                <X
                  :size="32"
                  color="white"
                />
              </div>
            </div>
          </div>
        </transition>
      </div>
      
      <div class="spacer-bottom" />
    </div>

    <!-- Bottom Action Bar -->
    <div class="bottom-action-bar glass-panel">
      <button
        class="confirm-btn"
        @click="$emit('confirm')"
      >
        <Wand2 :size="20" />
        <span>Confirm Selection ({{ confirmedCount }})</span>
      </button>


      <p class="disclaimer">
        All deleted photos will be moved to Recently Deleted in your Photos app.
      </p>
    </div>
  </div>
</template>

<style scoped>
.results-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-gray);
  overflow: hidden;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

h1 {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.smart-btn {
  background-color: var(--primary-blue);
  color: white;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
}

.scroll-content {
  flex: 1;
  overflow-y: scroll; /* Use generic scroll for better mobile feel */
  -webkit-overflow-scrolling: touch;
  padding: 16px;
}

/* Stats */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  background: var(--white);
  padding: 16px;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
}

.label {
  font-size: 10px;
  font-weight: 800;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.value {
  font-size: 28px;
  font-weight: 900;
  color: var(--text-primary);
  display: block;
}

.value.red {
  color: #EF4444;
}

/* Photo Card & Swiping */
.photo-card {
  position: relative;
  aspect-ratio: 1;
  background-color: #f3f4f6;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.photo-inner {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 10;
  background: #f3f4f6;
  transition: transform 0.1s ease-out; /* Real-time following is achieved by JS resetting this */
}

/* Remove transition when swiping manually for responsiveness */
.photo-inner[style*="translateX(0px)"] {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.swipe-bg {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 1;
}

.swipe-keep {
  background-color: #10B981;
  justify-content: flex-start;
}

.swipe-delete {
  background-color: #EF4444;
  justify-content: flex-end;
}

.control-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  padding: 6px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.ctrl-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
}

.ctrl-btn.active.keep {
  background: #10B981;
  color: white;
}

.ctrl-btn.active.delete {
  background: #EF4444;
  color: white;
}

.badge-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
}


.group-section {
  margin-bottom: 32px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 4px 0;
}

.spacer-bottom {
  height: 140px;
}

.bottom-action-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 20px 40px;
  z-index: 100;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
}

.confirm-btn {
  background-color: var(--primary-blue);
  color: white;
  padding: 16px;
  border-radius: 18px;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
}

.disclaimer {
  text-align: center;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 12px;
  opacity: 0.8;
}
</style>
