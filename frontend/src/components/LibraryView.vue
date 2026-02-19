<script setup>
import { ref } from 'vue';
import { Clock, HardDrive, Images, Trash2, ChevronRight } from 'lucide-vue-next';

// Mock data for history
const historyItems = ref([
  { id: 1, date: 'Feb 15, 2024', count: 124, saved: '372 MB', type: 'Camera Roll' },
  { id: 2, date: 'Feb 10, 2024', count: 56, saved: '168 MB', type: 'WhatsApp' },
  { id: 3, date: 'Feb 02, 2024', count: 210, saved: '630 MB', type: 'Camera Roll' },
]);

const stats = ref({
  totalSaved: '1.2 GB',
  photosProcessed: 1450,
  cleanUpRate: '42%'
});
</script>

<template>
  <div class="library-container">
    <header class="library-header">
      <h2>Storage Saved</h2>
      <div class="stats-grid">
        <div class="stat-card glass-panel">
          <HardDrive class="icon blue" :size="20" />
          <div class="stat-info">
            <span class="value">{{ stats.totalSaved }}</span>
            <span class="label">Total Saved</span>
          </div>
        </div>
        <div class="stat-card glass-panel">
          <Images class="icon purple" :size="20" />
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
        <button class="text-button">Clear All</button>
      </div>
      
      <div class="history-list">
        <div v-for="item in historyItems" :key="item.id" class="history-item glass-panel">
          <div class="history-icon">
            <Clock :size="18" />
          </div>
          <div class="history-details">
            <span class="date">{{ item.date }}</span>
            <span class="meta">{{ item.count }} photos • {{ item.type }}</span>
          </div>
          <div class="history-savings">
            <span class="amount">{{ item.saved }}</span>
            <ChevronRight :size="16" />
          </div>
        </div>
      </div>
    </section>

    <section class="keepers-section">
      <h3>The Keepers</h3>
      <div class="empty-state glass-panel">
        <Images :size="32" class="opacity-50" />
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
  transition: var(--transition);
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
