<script setup>
import { ChevronLeft, Wand2, ChevronDown, Download, Check, X } from 'lucide-vue-next'; // Added Check, X
import StatusBadge from './StatusBadge.vue';
import { computed, ref } from 'vue';

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

const emit = defineEmits(['back', 'confirm', 'view-group', 'toggle-keep', 'smart-clean']);

// Local state for collapsed groups
const collapsedGroups = ref({});

const toggleGroup = (groupTitle) => {
  collapsedGroups.value[groupTitle] = !collapsedGroups.value[groupTitle];
};

// Function to handle photo download
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
const photosToDeleteCount = computed(() => props.flatResults.filter(r => r.recommendation === 'Delete').length);

const getQualityLabel = (score) => {
  if (score > 0.8) return 'High Quality';
  if (score > 0.5) return 'Med Quality';
  return 'Low Quality';
};

const handleBulkAction = () => {
  // Logic: Mark all 'Review' items as 'Keep' as a simple bulk action demo
  const reviewItems = props.flatResults.filter(r => r.recommendation === 'Review');
  reviewItems.forEach(item => {
    emit('toggle-keep', item);
  });
  console.log("Bulk Action: Marked all 'Review' items as Keep");
};

const handleToggle = (item) => {
  emit('toggle-keep', item);
};

// Swipe Gestures
const touchStartX = ref(0);
const touchEndX = ref(0);
const SWIPE_THRESHOLD = 50;

const handleTouchStart = (e) => {
  touchStartX.value = e.touches[0].clientX;
};

const handleTouchEnd = (e, item) => {
  touchEndX.value = e.changedTouches[0].clientX;
  const deltaX = touchEndX.value - touchStartX.value;

  if (Math.abs(deltaX) > SWIPE_THRESHOLD) {
    if (deltaX > 0 && item.recommendation !== 'Keep') {
      // Swipe Right -> Keep
      emit('toggle-keep', item);
    } else if (deltaX < 0 && item.recommendation !== 'Delete') {
      // Swipe Left -> Delete
      emit('toggle-keep', item);
    }
  }
};
</script>

<template>
  <div class="results-view">
    <!-- Header -->
    <header class="top-bar">
      <button class="icon-btn" @click="$emit('back')">
        <ChevronLeft :size="24" />
      </button>
      <h1>Curation Results</h1>
      <button class="smart-btn" @click="$emit('smart-clean')">
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
          <span class="label">TO DELETE</span>
          <span class="value red">{{ photosToDeleteCount }}</span>
        </div>
      </div>

      <!-- Groups -->
      <div v-for="(group, idx) in groups" :key="idx" class="group-section">
        <div class="group-header clickable" @click="toggleGroup(group.title)">
          <h3>{{ group.title }}</h3>
          <div class="group-header-right">
            <span class="sub-text" v-if="group.items.length > 1">Best match selected</span>
            <ChevronDown :class="{ 'rotate-180': collapsedGroups[group.title] }" :size="20" class="chevron-icon" />
          </div>
        </div>

        <div v-if="!collapsedGroups[group.title]" class="photo-grid">
          <div 
            v-for="(item, i) in group.items" :key="i" 
            class="photo-card" 
            @click="$emit('view-group', group)"
            @touchstart="handleTouchStart"
            @touchend="handleTouchEnd($event, item)"
          >
            <img v-if="item.blobUrl" :src="item.blobUrl" class="photo-img" alt="Analyzed photo" />
            <div v-else class="img-placeholder">
               <span class="filename">{{ item.filename }}</span>
            </div>
            
            <!-- Download Button -->
            <button v-if="item.blobUrl" class="download-btn" @click.stop="downloadPhoto(item.blobUrl, item.filename)">
              <Download :size="16" color="white" />
            </button>

            <!-- Badge Overlay -->
            <div class="badge-overlay">
              <StatusBadge
                :status="item.error ? 'Error' : item.recommendation"
                :error-message="item.error"
              />
            </div>

            <!-- Manual Toggle Controls -->
            <div class="control-overlay" @click.stop>
              <button 
                class="ctrl-btn keep" 
                :class="{ active: item.recommendation === 'Keep' }"
                @click="handleToggle(item)"
              >
                <Check :size="14" />
              </button>
              <button 
                class="ctrl-btn delete" 
                :class="{ active: item.recommendation === 'Delete' }"
                @click="handleToggle(item)"
              >
                <X :size="14" />
              </button>
            </div>
            
            <!-- Quality Label -->
            <div class="quality-overlay">
              <StatusBadge :status="getQualityLabel(item.final_score)" type="label" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Safe space for bottom button -->
      <div class="spacer-bottom"></div>
    </div>

    <!-- Bottom Action Bar -->
    <div class="bottom-action-bar">
      <button class="confirm-btn" @click="$emit('confirm')">
        <Wand2 :size="20" />
        <span>Confirm {{ photosToDeleteCount }} Deletions</span>
      </button>
      <p class="disclaimer">All deleted photos will be moved to Recently Deleted in your Photos app.</p>
    </div>
  </div>
</template>

<style scoped>
.results-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-gray);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: var(--white);
  border-bottom: 1px solid #E5E7EB;
}

h1 {
  font-size: 18px;
  font-weight: 600;
}

.smart-btn {
  background-color: #DBEAFE;
  color: var(--primary-blue);
  padding: 8px 12px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.smart-btn:hover {
  background-color: #BFDBFE;
  transform: translateY(-1px);
}

/* Control Overlay */
.control-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px;
  border-radius: 8px;
  backdrop-filter: blur(4px);
}

.photo-card:hover .control-overlay {
  opacity: 1;
}

.badge-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  transition: opacity 0.2s ease;
}

.photo-card:hover .badge-overlay {
  opacity: 0;
}

.ctrl-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #E5E7EB;
  color: var(--text-secondary);
}

.ctrl-btn.active.keep {
  background: #10B981;
  color: white;
  border-color: #10B981;
}

.ctrl-btn.active.delete {
  background: #EF4444;
  color: white;
  border-color: #EF4444;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
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
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
}

.value.red {
  color: #EF4444;
}

/* Groups */
.group-section {
  margin-bottom: 32px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* Changed from baseline to center for vertical alignment with chevron */
  margin-bottom: 12px;
}

.group-header.clickable {
  cursor: pointer;
}

h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.group-header-right {
  display: flex;
  align-items: center;
  gap: 8px; /* Spacing between sub-text and chevron */
}

.sub-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.chevron-icon {
  transition: transform 0.2s ease; /* Smooth rotation */
}

.rotate-180 {
  transform: rotate(180deg);
}

/* Grid */
.photo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 2 columns */
  gap: 12px;
}

.photo-card {
  position: relative;
  aspect-ratio: 1; /* Square */
  background-color: #E5E7EB;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #D1D5DB;
  color: #6B7280;
  font-size: 10px;
  word-break: break-all;
  padding: 8px;
}

.badge-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
}

.quality-overlay {
  position: absolute;
  bottom: 8px;
  left: 8px;
}

.download-btn {
  position: absolute;
  top: 8px;
  left: 8px;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent black */
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10; /* Ensure it's above other elements */
  border: none;
  padding: 0;
}

.spacer-bottom {
  height: 100px;
}

/* Bottom Bar */
.bottom-action-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 16px 32px;
  background: var(--white);
  border-top: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.confirm-btn {
  background-color: var(--primary-blue);
  color: white;
  padding: 14px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.disclaimer {
  text-align: center;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
}
</style>
