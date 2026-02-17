<script setup>
import { CheckCircle2, Share2, Trash2 } from 'lucide-vue-next';
import { computed } from 'vue';

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      deletedCount: 0,
      spaceSaved: '0 MB'
    })
  }
});

const emit = defineEmits(['finish']);
</script>

<template>
  <div class="success-view">
    <div class="content">
      <div class="icon-circle">
        <CheckCircle2 :size="64" color="#10B981" />
      </div>
      
      <h1>Gallery Cleaned!</h1>
      <p class="description">You've successfully curated your latest photos and kept only the best shots.</p>
      
      <div class="stats-card">
        <div class="stat-item">
          <span class="stat-value text-red">{{ stats.deletedCount }}</span>
          <span class="stat-label">Photos Deleted</span>
        </div>
        <div class="divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.spaceSaved }}</span>
          <span class="stat-label">Space Saved</span>
        </div>
      </div>

      <div class="tips">
        <div class="tip-item">
          <Trash2 :size="18" />
          <span>Don't forget to empty your "Recently Deleted" folder.</span>
        </div>
      </div>
    </div>

    <div class="action-area">
      <button class="share-btn">
        <Share2 :size="20" />
        <span>Share Results</span>
      </button>
      <button class="finish-btn" @click="$emit('finish')">Finish</button>
    </div>
  </div>
</template>

<style scoped>
.success-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--white);
  padding: 32px 24px;
}

@media (min-width: 768px) {
  .success-view {
    padding: 64px 48px;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .stats-card {
    padding: 40px;
  }
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.icon-circle {
  width: 120px;
  height: 120px;
  background: #ECFDF5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

h1 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 40px;
}

.stats-card {
  width: 100%;
  background: #F9FAFB;
  border-radius: 24px;
  padding: 24px;
  display: flex;
  align-items: center;
  margin-bottom: 32px;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
}

.text-red {
  color: #EF4444;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.divider {
  width: 1px;
  height: 40px;
  background: #E5E7EB;
  margin: 0 24px;
}

.tips {
  background: #EFF6FF;
  border-radius: 16px;
  padding: 16px;
  width: 100%;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--primary-blue);
  font-size: 14px;
  font-weight: 500;
  text-align: left;
}

.action-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.finish-btn {
  background: var(--primary-blue);
  color: white;
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  width: 100%;
}

.share-btn {
  background: white;
  color: var(--text-primary);
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 16px;
  width: 100%;
  border: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
