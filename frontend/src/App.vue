<script setup>
import TopBar from './components/TopBar.vue';
import BottomNav from './components/BottomNav.vue';
import UploadCard from './components/UploadCard.vue';
import ActionButton from './components/ActionButton.vue';
import AnalyzingView from './components/AnalyzingView.vue';
import ResultsView from './components/ResultsView.vue';
import GroupDetailView from './components/GroupDetailView.vue';
import SuccessView from './components/SuccessView.vue';
import LibraryView from './components/LibraryView.vue';
import SettingsView from './components/SettingsView.vue';
import { Info } from 'lucide-vue-next';
import api from './api';
import { ref, onMounted, computed, watch } from 'vue';
import { estimateSpaceSaved } from './utils';

const selectedFiles = ref([]);
const currentView = ref('upload'); // 'upload' | 'analyzing' | 'results' | 'groupDetail' | 'success'
const analysisResults = ref(null); // This will store the grouped results from backend
const flatResults = computed(() => {
  if (!analysisResults.value) return [];
  return analysisResults.value.flatMap(group => group.items);
});
const fileBlobUrls = ref({});
const selectedGroup = ref(null);
const isAnalyzing = ref(false);
const apiError = ref(null);

// Settings and Theme
const settings = ref({
  theme: 'system'
});

const applyTheme = (theme) => {
  let activeTheme = theme;
  if (theme === 'system') {
    activeTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  
  if (activeTheme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

// Load results and settings from storage on mount
onMounted(() => {
  const storedResults = sessionStorage.getItem('analysisResults');
  if (storedResults) {
    try {
      analysisResults.value = JSON.parse(storedResults);
      currentView.value = 'results';
    } catch (e) {
      console.error("Failed to parse stored analysis results:", e);
      sessionStorage.removeItem('analysisResults');
    }
  }

  const savedSettings = localStorage.getItem('pickr_settings');
  if (savedSettings) {
    try {
      Object.assign(settings.value, JSON.parse(savedSettings));
    } catch (e) {
      console.error("Failed to load settings:", e);
    }
  }
  
  applyTheme(settings.value.theme);

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (settings.value.theme === 'system') {
      applyTheme('system');
    }
  });
});

// Watch for theme changes and apply
watch(() => settings.value.theme, (newTheme) => {
  applyTheme(newTheme);
});

// Watch for global settings changes from other components (if they use the same storage)
window.addEventListener('storage', (e) => {
  if (e.key === 'pickr_settings' && e.newValue) {
    settings.value = JSON.parse(e.newValue);
  }
});

const handleFiles = (files) => {
  selectedFiles.value = files;
  const newUrls = {};
  files.forEach(file => {
    newUrls[file.name] = URL.createObjectURL(file);
  });
  fileBlobUrls.value = newUrls;
};

const handleBackToUpload = () => {
  Object.values(fileBlobUrls.value).forEach(url => URL.revokeObjectURL(url));
  sessionStorage.removeItem('analysisResults');
  currentView.value = 'upload';
  selectedFiles.value = [];
  fileBlobUrls.value = {};
};

const analyzePhotos = async () => {
  if (selectedFiles.value.length === 0) {
    alert("Please select photos first.");
    return;
  }
  
  isAnalyzing.value = true;
  apiError.value = null;
  currentView.value = 'analyzing';
  
  const formData = new FormData();
  selectedFiles.value.forEach(file => {
    formData.append('files', file);
  });

  try {
    // Artificial delay for smooth transition
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const response = await api.post('/analyze', formData);
    
    // The backend returns groups: [{ title: string, items: Array }]
    const groupedResults = (response.data.analysis_results || []).map(group => ({
      ...group,
      items: group.items.map(item => ({
        ...item,
        blobUrl: fileBlobUrls.value[item.filename],
        isConfirmed: false // Initial state
      }))
    }));
    
    analysisResults.value = groupedResults;
    sessionStorage.setItem('analysisResults', JSON.stringify(groupedResults));
    currentView.value = 'results';
  } catch (error) {
    console.error("Analysis failed:", error);
    apiError.value = error.message || "Failed to analyze photos.";
    currentView.value = 'upload';
  } finally {
    isAnalyzing.value = false;
  }
};

// --- Phase 1 Handlers ---

const undoStack = ref([]);

const saveResults = () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    if (analysisResults.value) {
      sessionStorage.setItem('analysisResults', JSON.stringify(analysisResults.value));
    }
  }, 1000);
};

const pushToUndoStack = () => {
  if (analysisResults.value) {
    // Keep stack size reasonable
    if (undoStack.value.length >= 10) {
      undoStack.value.shift();
    }
    undoStack.value.push(JSON.parse(JSON.stringify(analysisResults.value)));
  }
};

const handleUndo = () => {
  if (undoStack.value.length > 0) {
    analysisResults.value = undoStack.value.pop();
    saveResults();
  }
};

const handleUpdateStatus = (item, status) => {
  if (!analysisResults.value) return;
  pushToUndoStack();
  for (const group of analysisResults.value) {
    const target = group.items.find(r => r.filename === item.filename);
    if (target) {
      target.recommendation = status;
      target.isConfirmed = true;
      break;
    }
  }
  saveResults();
};

const handleSetBest = (item) => {
  if (!analysisResults.value) return;
  pushToUndoStack();
  for (const group of analysisResults.value) {
    const hasItem = group.items.some(r => r.filename === item.filename);
    if (hasItem) {
      group.items.forEach(r => {
        r.isBest = r.filename === item.filename;
        r.isConfirmed = true; // Choosing a best shot confirms the decision
      });
      break;
    }
  }
  saveResults();
};

const handleSmartClean = () => {
  if (!analysisResults.value) return;
  pushToUndoStack();
  
  analysisResults.value = analysisResults.value.map(group => {
    if (group.items.length <= 1) return group;
    
    return {
      ...group,
      items: group.items.map(item => ({
        ...item,
        recommendation: item.isBest ? 'Keep' : 'Delete',
        isConfirmed: true // Smart clean confirms everything in the group
      }))

    };
  });
  
  saveResults();
};

const confirmDeletions = () => {
  // Save to history before showing success
  const stats = successStats.value;
  const historyEntry = {
    id: Date.now(),
    date: new Date().toISOString(),
    count: flatResults.value.length,
    deleted: stats.deletedCount,
    saved: stats.spaceSaved,
    type: 'Manual Curation'
  };

  const history = JSON.parse(localStorage.getItem('pickr_history') || '[]');
  history.unshift(historyEntry);
  localStorage.setItem('pickr_history', JSON.stringify(history.slice(0, 50))); // Keep last 50

  currentView.value = 'success';
};

const handleFinish = () => {
  handleBackToUpload();
};

const handleViewGroup = (group) => {
  selectedGroup.value = group;
  currentView.value = 'groupDetail';
};

const handleNextGroup = () => {
  if (!analysisResults.value || !selectedGroup.value) {
    currentView.value = 'results';
    return;
  }
  
  const currentIndex = analysisResults.value.findIndex(g => g.title === selectedGroup.value.title);
  if (currentIndex !== -1 && currentIndex < analysisResults.value.length - 1) {
    selectedGroup.value = analysisResults.value[currentIndex + 1];
  } else {
    currentView.value = 'results';
    selectedGroup.value = null;
  }
};

const handleNavigate = (view) => {
  currentView.value = view;
};

const successStats = computed(() => {
  const results = flatResults.value || [];
  if (results.length === 0) return { deletedCount: 0, spaceSaved: '0 MB' };
  const deleted = results.filter(r => r.recommendation === 'Delete').length;
  return {
    deletedCount: deleted,
    spaceSaved: estimateSpaceSaved(deleted)
  };
});

let saveTimeout = null;
</script>

<template>
  <div class="app-container container">
    <transition
      name="fade"
      mode="out-in"
    >
      <div
        :key="currentView"
        class="view-wrapper"
      >
        <!-- Upload View -->
        <template v-if="currentView === 'upload'">
          <TopBar />
          <main class="content-area">
            <!-- Error Banner -->
            <div 
              v-if="apiError" 
              class="error-banner glass-panel"
            >
              <div class="error-content">
                <Info :size="16" />
                <span>{{ apiError }}</span>
              </div>
              <button 
                class="close-error" 
                @click="apiError = null"
              >
                &times;
              </button>
            </div>

            <UploadCard @files-selected="handleFiles" />
            <div class="info-text">
              <Info :size="14" />
              <span>SUPPORTS JPG, PNG, HEIC</span>
            </div>
            <div class="action-area">
              <ActionButton @click="analyzePhotos" />
            </div>
          </main>
          <BottomNav
            :active-view="currentView"
            @navigate="handleNavigate"
          />
        </template>

        <!-- Library View -->
        <template v-else-if="currentView === 'library'">
          <TopBar />
          <main class="content-area">
            <LibraryView />
          </main>
          <BottomNav
            :active-view="currentView"
            @navigate="handleNavigate"
          />
        </template>

        <!-- Settings View -->
        <template v-else-if="currentView === 'settings'">
          <TopBar />
          <main class="content-area">
            <SettingsView />
          </main>
          <BottomNav
            :active-view="currentView"
            @navigate="handleNavigate"
          />
        </template>

        <!-- Analyzing View -->
        <template v-else-if="currentView === 'analyzing'">
          <AnalyzingView />
        </template>

        <!-- Results View -->
        <template v-if="currentView === 'results'">
          <ResultsView 
            :groups="analysisResults"
            :flat-results="flatResults"
            :can-undo="undoStack.length > 0"
            @back="handleBackToUpload"
            @confirm="confirmDeletions"
            @view-group="handleViewGroup"
            @update-status="handleUpdateStatus"
            @smart-clean="handleSmartClean"
            @set-best="handleSetBest"
            @undo="handleUndo"
          />
        </template>

        <!-- Group Detail View -->
        <template v-else-if="currentView === 'groupDetail'">
          <GroupDetailView
            :group="selectedGroup"
            @back="handleNextGroup"
            @update-status="handleUpdateStatus"
            @set-best="handleSetBest"
          />
        </template>

        <!-- Success View -->
        <template v-else-if="currentView === 'success'">
          <SuccessView 
            :stats="successStats"
            @finish="handleFinish"
          />
        </template>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-gray);
  overflow: hidden; /* Prevent double scrollbars with view-wrapper */
}

.view-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 16px;
  overflow-y: auto;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

.info-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 8px;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
  opacity: 0.7;
}

.action-area {
  margin-top: auto;
  margin-bottom: 24px;
  padding: 0 16px;
}
.error-banner {
  margin-top: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 12px;
  color: #EF4444;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
}

.close-error {
  font-size: 20px;
  color: #EF4444;
  opacity: 0.6;
  padding: 4px;
}

.close-error:hover {
  opacity: 1;
}
</style>
