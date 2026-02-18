<script setup>
import { ref, onMounted, watch } from 'vue';
import { Shield, Zap, Moon, Sun, Monitor, Trash2, Info, ChevronRight } from 'lucide-vue-next';

const settings = ref({
  similarityThreshold: 85,
  blurThreshold: 60,
  autoAdvance: true,
  deletionStrategy: 'trash', // 'trash' | 'permanent'
  theme: 'system' // 'light' | 'dark' | 'system'
});

// Load settings from localStorage
onMounted(() => {
  const saved = localStorage.getItem('pickr_settings');
  if (saved) {
    try {
      Object.assign(settings.value, JSON.parse(saved));
    } catch (e) {
      console.error("Failed to load settings:", e);
    }
  }
});

// Watch for changes and save
watch(settings, (newVal) => {
  localStorage.setItem('pickr_settings', JSON.stringify(newVal));
}, { deep: true });

const clearStorage = () => {
  if (confirm("Clear all curation history and reset settings?")) {
    localStorage.removeItem('pickr_settings');
    sessionStorage.removeItem('analysisResults');
    location.reload();
  }
};
</script>

<template>
  <div class="settings-container">
    <header class="settings-header">
      <h2>Settings</h2>
    </header>

    <section class="settings-group">
      <div class="group-label">AI DETECTION</div>
      <div class="settings-card glass-panel">
        <div class="setting-item">
          <div class="setting-info">
            <span class="title">Similarity Threshold</span>
            <span class="description">How strict to be with duplicates</span>
          </div>
          <div class="setting-control">
            <input type="range" v-model="settings.similarityThreshold" min="50" max="95" class="slider" />
            <span class="value">{{ settings.similarityThreshold }}%</span>
          </div>
        </div>
        
        <div class="divider"></div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="title">Blur Sensitivity</span>
            <span class="description">How strict to be with blurry shots</span>
          </div>
          <div class="setting-control">
            <input type="range" v-model="settings.blurThreshold" min="10" max="90" class="slider" />
            <span class="value">{{ settings.blurThreshold }}%</span>
          </div>
        </div>
      </div>
    </section>

    <section class="settings-group">
      <div class="group-label">WORKFLOW</div>
      <div class="settings-card glass-panel">
        <div class="setting-item">
          <div class="setting-info">
            <span class="title">Auto-Advance</span>
            <span class="description">Move to next group after selecting best</span>
          </div>
          <div class="setting-control">
            <label class="switch">
              <input type="checkbox" v-model="settings.autoAdvance">
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
        
        <div class="divider"></div>

        <div class="setting-item">
          <div class="setting-info">
            <span class="title">Deletion Strategy</span>
          </div>
          <div class="setting-control">
            <select v-model="settings.deletionStrategy" class="select-input">
              <option value="trash">Move to Trash</option>
              <option value="permanent">Permanent Delete</option>
            </select>
          </div>
        </div>
      </div>
    </section>

    <section class="settings-group">
      <div class="group-label">APPEARANCE</div>
      <div class="theme-selector glass-panel">
        <button 
          v-for="mode in ['light', 'dark', 'system']" 
          :key="mode"
          class="theme-btn"
          :class="{ active: settings.theme === mode }"
          @click="settings.theme = mode"
        >
          <Sun v-if="mode === 'light'" :size="18" />
          <Moon v-if="mode === 'dark'" :size="18" />
          <Monitor v-if="mode === 'system'" :size="18" />
          <span>{{ mode.charAt(0).toUpperCase() + mode.slice(1) }}</span>
        </button>
      </div>
    </section>

    <section class="settings-group">
      <div class="group-label">DANGER ZONE</div>
      <button class="danger-button glass-panel" @click="clearStorage">
        <Trash2 :size="18" />
        <span>Clear Storage & Reset</span>
      </button>
    </section>

    <footer class="settings-footer">
      <span class="version">Pickr v1.0.0</span>
      <div class="footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-header h2 {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
}

.settings-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-label {
  font-size: 11px;
  font-weight: 800;
  color: var(--text-secondary);
  letter-spacing: 1px;
  padding-left: 4px;
}

.settings-card {
  border-radius: 20px;
  overflow: hidden;
}

.setting-item {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-info .title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.setting-info .description {
  font-size: 12px;
  color: var(--text-secondary);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.divider {
  height: 1px;
  background: var(--glass-border);
  margin: 0 16px;
}

/* Slider styling */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100px;
  height: 4px;

  background: #E5E7EB;
  border-radius: 2px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--primary-blue);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.value {
  font-size: 13px;
  font-weight: 800;
  color: var(--primary-blue);
  min-width: 35px;
  text-align: right;
}

/* Switch styling */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #E5E7EB;
  transition: .4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--primary-blue);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* Select styling */
.select-input {
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  outline: none;
}

/* Theme selector */
.theme-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  padding: 6px;
  border-radius: 16px;
  gap: 4px;
}

.theme-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px;
  border-radius: 12px;
  color: var(--text-secondary);
}

.theme-btn.active {
  background: var(--white);
  color: var(--primary-blue);
  box-shadow: var(--shadow-sm);
}

.theme-btn span {
  font-size: 11px;
  font-weight: 700;
}

/* Danger Zone */
.danger-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  border-radius: 16px;
  color: #EF4444;
  font-weight: 700;
  font-size: 14px;
}

.settings-footer {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-bottom: 40px;
}

.version {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  opacity: 0.6;
}

.footer-links {
  display: flex;
  gap: 16px;
}

.footer-links a {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-blue);
  text-decoration: none;
}
</style>
