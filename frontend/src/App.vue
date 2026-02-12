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
import { ref, onMounted } from 'vue';
import axios from 'axios';

const selectedFiles = ref([]);
const currentView = ref('upload'); // 'upload' | 'analyzing' | 'results' | 'groupDetail' | 'success'
const analysisResults = ref(null);
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
    
    const resultsWithBlobs = (response.data.analysis_results || []).map(result => ({
      ...result,
      blobUrl: fileBlobUrls.value[result.filename],
      isBest: false // New field for Phase 1
    }));
    
    analysisResults.value = resultsWithBlobs;
    sessionStorage.setItem('analysisResults', JSON.stringify(resultsWithBlobs));
    currentView.value = 'results';
  } catch (error) {
    console.error("Analysis failed:", error);
    alert("Analysis failed.");
    currentView.value = 'upload';
  }
};

// --- Phase 1 Handlers ---

const handleToggleKeep = (item) => {
  const target = analysisResults.value.find(r => r.filename === item.filename);
  if (target) {
    target.recommendation = target.recommendation === 'Keep' ? 'Delete' : 'Keep';
    sessionStorage.setItem('analysisResults', JSON.stringify(analysisResults.value));
  }
};

const handleSetBest = (item) => {
  // Clear other "best" in the same group (for now we group by recommendation)
  analysisResults.value.forEach(r => {
     if (r.recommendation === item.recommendation) {
       r.isBest = (r.filename === item.filename);
     }
  });
  sessionStorage.setItem('analysisResults', JSON.stringify(analysisResults.value));
};

const confirmDeletions = () => {
  currentView.value = 'success';
};

const handleFinish = () => {
  handleBackToUpload();
};

const handleViewGroup = (group) => {
  selectedGroup.value = group;
  currentView.value = 'groupDetail';
};

const handleBackToResults = () => {
  currentView.value = 'results';
  selectedGroup.value = null;
};

const successStats = computed(() => {
  if (!analysisResults.value) return { deletedCount: 0, spaceSaved: '0 MB' };
  const deleted = analysisResults.value.filter(r => r.recommendation === 'Delete').length;
  // Mock space saving: assume 3MB per photo
  return {
    deletedCount: deleted,
    spaceSaved: `${deleted * 3} MB`
  };
});
</script>

<template>
  <div class="app-container">
    
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
        :results="analysisResults"
        @back="handleBackToUpload"
        @confirm="confirmDeletions"
        @view-group="handleViewGroup"
        @toggle-keep="handleToggleKeep"
      />
    </template>

    <!-- Group Detail View -->
    <template v-else-if="currentView === 'groupDetail'">
      <GroupDetailView
        :group="selectedGroup"
        @back="handleBackToResults"
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
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-gray);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 16px;
  overflow-y: auto;
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
