<script setup>
import { CheckCircle, Trash2, Eye, AlertCircle } from 'lucide-vue-next';

const props = defineProps({
  status: {
    type: String,
    required: false,
    default: 'Review',
    validator: (value) => !value || ['Keep', 'Delete', 'Review', 'High Quality', 'Med Quality', 'Low Quality', 'Error'].includes(value)
  },
  type: {
    type: String,
    default: 'badge' // 'badge' or 'label'
  },
  errorMessage: {
    type: String,
    default: null
  }
});

const getIcon = () => {
  switch (props.status) {
    case 'Keep': return CheckCircle;
    case 'Delete': return Trash2;
    case 'Review': return Eye;
    case 'Error': return AlertCircle;
    default: return null;
  }
};

const getColorClass = () => {
  switch (props.status) {
    case 'Keep': return 'bg-green';
    case 'Delete': return 'bg-red';
    case 'Review': return 'bg-yellow';
    case 'Error': return 'bg-gray-dark'; // A distinct color for errors
    default: return 'bg-gray';
  }
};
</script>

<template>
  <div v-if="['Keep', 'Delete', 'Review', 'Error'].includes(status || 'Review')" class="status-badge" :class="getColorClass()">
    <component :is="getIcon()" :size="12" stroke-width="3" />
    <span v-if="status !== 'Error'">{{ status.toUpperCase() }}</span>
    <span v-else>{{ errorMessage ? 'ERROR: ' + errorMessage.toUpperCase() : 'ERROR' }}</span>
  </div>
  
  <div v-else class="quality-label">
    {{ (status || 'Unknown').toUpperCase() }}
  </div>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 800;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.quality-label {
  display: inline-block;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
}

/* Colors */
.bg-green { background-color: #10B981; }
.bg-red { background-color: #EF4444; }
.bg-yellow { background-color: #F59E0B; }
.bg-gray { background-color: #6B7280; }
.bg-gray-dark { background-color: #4B5563; } /* New color for errors */
</style>
