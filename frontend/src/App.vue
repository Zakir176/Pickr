<script setup>
import TopBar from './components/TopBar.vue';
import BottomNav from './components/BottomNav.vue';
import UploadCard from './components/UploadCard.vue';
import ActionButton from './components/ActionButton.vue';
import AnalyzingView from './components/AnalyzingView.vue';
import ResultsView from './components/ResultsView.vue';
import GroupDetailView from './components/GroupDetailView.vue';
import SuccessView from './components/SuccessView.vue'; // Added SuccessView
import { Info } from 'lucide-vue-next';
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const selectedFiles = ref([]);
const currentView = ref('upload'); // 'upload' | 'analyzing' | 'results' | 'groupDetail' | 'success'
const analysisResults = ref(null); // This will store the grouped results from backend
const flatResults = computed(() => {
  if (!analysisResults.value) return [];
  return analysisResults.value.flatMap(group => group.items);
});
const fileBlobUrls = ref({});
const selectedGroup = ref(null);

// Load results from sessionStorage on mount
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
  
  currentView.value = 'analyzing';
  const formData = new FormData();
  selectedFiles.value.forEach(file => {
    formData.append('files', file);
  });

  try {
    await new Promise(resolve => setTimeout(resolve, 1500));
    const response = await axios.post('/analyze', formData);
    
    // The backend returns groups: [{ title: string, items: Array }]
    const groupedResults = (response.data.analysis_results || []).map(group => ({
      ...group,
      items: group.items.map(item => ({
        ...item,
        blobUrl: fileBlobUrls.value[item.filename]
      }))
    }));
    
    analysisResults.value = groupedResults;
    sessionStorage.setItem('analysisResults', JSON.stringify(groupedResults));
    currentView.value = 'results';
  } catch (error) {
    console.error("Analysis failed:", error);
    alert("Analysis failed.");
    currentView.value = 'upload';
  }
};

// --- Phase 1 Handlers ---

const handleToggleKeep = (item) => {
  // Find the item in the grouped results
  analysisResults.value.forEach(group => {
    const target = group.items.find(r => r.filename === item.filename);
    if (target) {
      target.recommendation = target.recommendation === 'Keep' ? 'Delete' : 'Keep';
    }
  });
  saveResults();
};

const handleSetBest = (item) => {
  // Find the group containing this item
  analysisResults.value.forEach(group => {
    const hasItem = group.items.some(r => r.filename === item.filename);
    if (hasItem) {
      group.items.forEach(r => {
        r.isBest = (r.filename === item.filename);
      });
    }
  });
  saveResults();
};

const confirmDeletions = () => {
  currentView.value = 'success';
};

const handleSmartClean = () => {
  if (!analysisResults.value) return;
  
  analysisResults.value.forEach(group => {
    // If it's a similar set (multiple items)
    if (group.items.length > 1) {
      // 1. Ensure the 'Best Shot' is marked Keep
      // 2. Mark all others as Delete
      group.items.forEach(item => {
        item.recommendation = item.isBest ? 'Keep' : 'Delete';
      });
    }
  });
  
  saveResults();
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

const handleBackToResults = () => {
  currentView.value = 'results';
  selectedGroup.value = null;
};

const successStats = computed(() => {
  const results = flatResults.value || [];
  if (results.length === 0) return { deletedCount: 0, spaceSaved: '0 MB' };
  const deleted = results.filter(r => r.recommendation === 'Delete').length;
  // Mock space saving: assume 3MB per photo
  return {
    deletedCount: deleted,
    spaceSaved: `${deleted * 3} MB`
  };
});

// Debounced save to sessionStorage
let saveTimeout = null;
const saveResults = () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    if (analysisResults.value) {
      sessionStorage.setItem('analysisResults', JSON.stringify(analysisResults.value));
    }
  }, 1000);
};
</script>

<template>
  <div class="app-container">
    <transition name="fade" mode="out-in">
      <div :key="currentView" class="view-wrapper">
        <!-- Upload View -->
        <template v-if="currentView === 'upload'">
          <TopBar />
          <main class="content-area">
            <UploadCard @files-selected="handleFiles" />
            <div class="info-text">
              <Info :size="14" />
              <span>SUPPORTS JPG, PNG, HEIC</span>
            </div>
            <div class="action-area">
              <ActionButton @click="analyzePhotos" />
            </div>
          </main>
          <BottomNav />
        </template>

        <!-- Analyzing View -->
        <template v-else-if="currentView === 'analyzing'">
          <AnalyzingView />
        </template>

        <!-- Results View -->
        <template v-else-if="currentView === 'results'">
          <ResultsView 
            :groups="analysisResults"
            :flat-results="flatResults"
            @back="handleBackToUpload"
            @confirm="confirmDeletions"
            @view-group="handleViewGroup"
            @toggle-keep="handleToggleKeep"
            @smart-clean="handleSmartClean"
          />
        </template>

        <!-- Group Detail View -->
        <template v-else-if="currentView === 'groupDetail'">
          <GroupDetailView
            :group="selectedGroup"
            @back="handleNextGroup"
            @toggle-keep="handleToggleKeep"
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
  max-width: 800px;
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
</style>
