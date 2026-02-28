<script setup>
import { ref, onMounted, computed } from 'vue';
import { Clock, HardDrive, Images, ChevronRight } from 'lucide-vue-next';
import { formatSize, formatDate } from '../utils';

const historyItems = ref([]);

const stats = computed(() => {
  const totalS = historyItems.value.reduce((acc, item) => {
    // Extract numeric MB from string like "372 MB"
    const mb = parseFloat(item.saved) || 0;
    return acc + mb;
  }, 0);
  
  const totalP = historyItems.value.reduce((acc, item) => acc + (item.count || 0), 0);
  const totalD = historyItems.value.reduce((acc, item) => acc + (item.deleted || 0), 0);
  
  return {
    totalSaved: formatSize(totalS),
    photosProcessed: totalP,
    cleanUpRate: totalP > 0 ? `${Math.round((totalD / totalP) * 100)}%` : '0%'
  };
});

onMounted(() => {
  const saved = localStorage.getItem('pickr_history');
  if (saved) {
    try {
      historyItems.value = JSON.parse(saved);
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  }
});

const clearHistory = () => {
  if (confirm("Clear all curation history?")) {
    historyItems.value = [];
    localStorage.removeItem('pickr_history');
  }
};
</script>

<template>
  <div class="library-container">
    <header class="library-header">
      <h2>Storage Saved</h2>
      <div class="stats-grid">
        <div class="stat-card glass-panel">
          <HardDrive
            class="icon blue"
            :size="20"
          />
          <div class="stat-info">
            <span class="value">{{ stats.totalSaved }}</span>
            <span class="label">Total Saved</span>
          </div>
        </div>
        <div class="stat-card glass-panel">
          <Images
            class="icon purple"
            :size="20"
          />
          <div class="stat-info">
            <span class="value">{{ stats.photosProcessed }}</span>
            <span class="label">Processed</span>
          </div>
        </div>
      </div>
    </header>

    <section class="history-section">
      <div class="section-header">
        <h3>Curation History</h3>
        <button 
          v-if="historyItems.length > 0"
          class="text-button"
          @click="clearHistory"
        >
          Clear All
        </button>
      </div>
      
      <div 
        v-if="historyItems.length > 0"
        class="history-list"
      >
        <div
          v-for="item in historyItems"
          :key="item.id"
          class="history-item glass-panel"
        >
          <div class="history-icon">
            <Clock :size="18" />
          </div>
          <div class="history-details">
            <span class="date">{{ formatDate(item.date) }}</span>
            <span class="meta">{{ item.count }} photos • {{ item.type }}</span>
          </div>
          <div class="history-savings">
            <span class="amount">{{ item.saved }}</span>
            <ChevronRight :size="16" />
          </div>
        </div>
      </div>
      <div 
        v-else 
        class="empty-state glass-panel"
      >
        <Clock :size="32" class="opacity-50" />
        <p>No history yet. Start curating!</p>
      </div>
    </section>

    <section class="keepers-section">
      <h3>The Keepers</h3>
      <div class="empty-state glass-panel">
        <Images
          :size="32"
          class="opacity-50"
        />
        <p>No featured photos yet. Keep curating!</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.library-container {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.library-header h2 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-card {
  padding: 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-info .value {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
}

.stat-info .label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.icon.blue { color: var(--primary-blue); }
.icon.purple { color: #A855F7; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.text-button {
  font-size: 12px;
  font-weight: 700;
  color: var(--primary-blue);
  padding: 4px 8px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px 16px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.history-item:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow);
}

.history-item:active {
  transform: scale(0.98);
}

.history-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-blue);
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-details .date {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.history-details .meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.history-savings {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.history-savings .amount {
  font-size: 13px;
  font-weight: 800;
  color: #10B981; /* Emerald green */
}

.empty-state {
  padding: 40px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state p {
  font-size: 14px;
  font-weight: 600;
}

.opacity-50 { opacity: 0.5; }
</style>
