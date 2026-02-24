<script setup>
import { Star } from 'lucide-vue-next';

const props = defineProps({
  isBest: {
    type: Boolean,
    default: false
  },
  interactive: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['toggle']);

const handleClick = (e) => {
  if (props.interactive) {
    e.stopPropagation();
    emit('toggle');
  }
};
</script>

<template>
  <button 
    class="best-shot-indicator" 
    :class="{ active: isBest, readonly: !interactive }"
    :aria-label="isBest ? 'Unmark as best shot' : 'Mark as best shot'"
    :disabled="!interactive"
    @click="handleClick"
  >
    <Star 
      :size="16" 
      :fill="isBest ? '#FBBF24' : 'none'" 
      :color="isBest ? '#FBBF24' : 'white'" 
      :class="{ 'glow-star': isBest }"
    />
    <span v-if="isBest">Best Shot</span>
  </button>
</template>

<style scoped>
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
  cursor: pointer;
}

.best-shot-indicator.readonly {
  cursor: default;
  pointer-events: none;
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
</style>
