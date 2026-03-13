<script setup>
import { ref, onMounted, computed } from 'vue';
import { Clock, HardDrive, Images, ChevronRight, Search, Filter } from 'lucide-vue-next';
import { formatSize, formatDate } from '../utils';

const historyItems = ref([]);
const keepers = ref([]);
const searchQuery = ref('');
const dateFilter = ref('all');

const filteredHistory = computed(() => {
  let items = historyItems.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    items = items.filter(item => 
      formatDate(item.date).toLowerCase().includes(q) || 
      item.type.toLowerCase().includes(q)
    );
  }
  
  if (dateFilter.value !== 'all') {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    items = items.filter(item => {
      const d = new Date(item.date);
      if (dateFilter.value === 'today') return d >= today;
      if (dateFilter.value === 'week') {
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        return d >= weekAgo;
      }
      if (dateFilter.value === 'month') {
        const monthAgo = new Date(today);
        monthAgo.setMonth(monthAgo.getMonth() - 1);
        return d >= monthAgo;
      }
      return true;
    });
  }
  
  return items;
});

const stats = computed(() => {
  const totalS = historyItems.value.reduce((acc, item) => {
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
  const savedHistory = localStorage.getItem('pickr_history');
  if (savedHistory) {
    try {
      historyItems.value = JSON.parse(savedHistory);
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  }

  const savedKeepers = localStorage.getItem('pickr_keepers');
  if (savedKeepers) {
    try {
      keepers.value = JSON.parse(savedKeepers);
    } catch (e) {
      console.error("Failed to load keepers:", e);
    }
  }
});

const clearHistory = () => {
  if (confirm("Clear all curation history?")) {
    historyItems.value = [];
    localStorage.removeItem('pickr_history');
  }
};

const removeKeeper = (keeper) => {
  keepers.value = keepers.value.filter(k => k.filename !== keeper.filename);
  localStorage.setItem('pickr_keepers', JSON.stringify(keepers.value));
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

      <!-- Search and Filter -->
      <div class="filter-bar" v-if="historyItems.length > 0">
        <div class="search-input-wrapper glass-panel">
          <Search :size="16" class="search-icon" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search history..." 
            class="search-input"
          >
        </div>
        <div class="filter-select-wrapper glass-panel">
          <Filter :size="16" class="filter-icon" />
          <select v-model="dateFilter" class="filter-select">
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
      </div>
      
      <div 
        v-if="filteredHistory.length > 0"
        class="history-list"
      >
        <div
          v-for="item in filteredHistory"
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
      <div 
        v-if="keepers.length > 0"
        class="keepers-grid"
      >
        <div
          v-for="keeper in keepers"
          :key="keeper.filename"
          class="keeper-card glass-panel"
        >
          <div class="keeper-thumbnail">
            <img 
              v-if="keeper.thumbnail" 
              :src="keeper.thumbnail" 
              class="keeper-img" 
              alt="Thumbnail"
            >
            <Images v-else :size="32" color="#3B82F6" />
          </div>
          <div class="keeper-info">
            <span class="filename">{{ keeper.filename }}</span>
            <span class="score">Score: {{ Math.round(keeper.score * 100) }}%</span>
          </div>
          <button 
            class="remove-keeper" 
            @click="removeKeeper(keeper)"
          >
            &times;
          </button>
        </div>
      </div>
      <div 
        v-else 
        class="empty-state glass-panel"
      >
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

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 12px;
}

.search-input {
  background: transparent;
  border: none;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  width: 100%;
  outline: none;
}

.search-icon, .filter-icon {
  color: var(--text-secondary);
  opacity: 0.6;
}

.filter-select-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 12px;
}

.filter-select {
  background: transparent;
  border: none;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  outline: none;
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
  gap: 4px;
  color: var(--text-secondary);
}

.history-savings .amount {
  font-size: 14px;
  font-weight: 800;
  color: #10B981;
}

.keepers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.keeper-card {
  padding: 12px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  transition: transform 0.3s ease;
}

.keeper-card:hover {
  transform: translateY(-4px);
}

.keeper-thumbnail {
  aspect-ratio: 1;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden; /* For images */
}

.keeper-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.keeper-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.keeper-info .filename {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.keeper-info .score {
  font-size: 10px;
  color: var(--text-secondary);
}

.remove-keeper {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.1);
  border-radius: 50%;
  color: var(--text-secondary);
  font-size: 14px;
}

.empty-state {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  color: var(--text-secondary);
  border-radius: 20px;
}

.opacity-50 {
  opacity: 0.5;
}
</style>
