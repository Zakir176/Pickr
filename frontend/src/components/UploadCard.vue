<script setup>
import { Camera } from 'lucide-vue-next';
import { ref } from 'vue';

const fileInput = ref(null);
const emit = defineEmits(['files-selected']);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const files = Array.from(event.target.files);
  if (files.length > 0) {
    emit('files-selected', files);
  }
};
</script>

<template>
  <div class="upload-card">
    <div class="icon-circle">
      <Camera :size="48" color="#3B82F6" />
      <div class="plus-badge">+</div>
    </div>
    
    <h2>Select Photos</h2>
    <p>Upload photos to analyze quality<br>and find duplicates automatically</p>
    
    <button class="browse-btn" @click="triggerFileInput">
      Browse Gallery
    </button>
    
    <input 
      type="file" 
      ref="fileInput" 
      multiple 
      accept="image/*" 
      class="hidden-input"
      @change="handleFileChange"
    />
  </div>
</template>

<style scoped>
.upload-card {
  background-color: var(--white);
  border-radius: 24px;
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: var(--shadow-sm);
  margin: 16px;
  flex-grow: 1; /* Fill available space */
  justify-content: center;
  transition: var(--transition);
}

@media (min-width: 768px) {
  .upload-card {
    padding: 80px 48px;
    max-width: 600px;
    margin: 40px auto;
    border: 1px solid var(--glass-border);
  }
}

.icon-circle {
  width: 96px;
  height: 96px;
  background-color: #EFF6FF; /* Blue 50 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  position: relative;
}

.plus-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  color: var(--primary-blue);
  font-weight: bold;
  font-size: 20px;
}

h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 32px;
}

.browse-btn {
  background-color: #EFF6FF;
  color: var(--primary-blue);
  font-weight: 600;
  padding: 12px 32px;
  border-radius: 100px;
  font-size: 14px;
  transition: background-color 0.2s;
}

.browse-btn:hover {
  background-color: #DBEAFE;
}

.hidden-input {
  display: none;
}
</style>
