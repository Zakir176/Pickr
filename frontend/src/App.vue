<script setup>
import TopBar from './components/TopBar.vue';
import BottomNav from './components/BottomNav.vue';
import UploadCard from './components/UploadCard.vue';
import ActionButton from './components/ActionButton.vue';
import AnalyzingView from './components/AnalyzingView.vue';
import ResultsView from './components/ResultsView.vue';
import GroupDetailView from './components/GroupDetailView.vue';
import { Info } from 'lucide-vue-next';
import { ref } from 'vue';
import axios from 'axios';

const selectedFiles = ref([]);
const currentView = ref('upload'); // 'upload' | 'analyzing' | 'results' | 'groupDetail'
const analysisResults = ref(null);
const fileBlobUrls = ref({}); // Maps filename to blob URL
const selectedGroup = ref(null); // For the detail view

const handleFiles = (files) => {
  console.log("Files selected:", files);
  selectedFiles.value = files;

  // Create blob URLs for preview
  const newUrls = {};
  files.forEach(file => {
    newUrls[file.name] = URL.createObjectURL(file);
  });
  fileBlobUrls.value = newUrls;
};

const handleBackToUpload = () => {
  // Revoke old blob URLs to prevent memory leaks
  Object.values(fileBlobUrls.value).forEach(url => URL.revokeObjectURL(url));
  
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
    await new Promise(resolve => setTimeout(resolve, 2000));

    const response = await axios.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    console.log(response.data);
    
    // Merge blob URLs with analysis results
    const resultsWithBlobs = (response.data.analysis_results || []).map(result => ({
      ...result,
      blobUrl: fileBlobUrls.value[result.filename]
    }));
    
    analysisResults.value = resultsWithBlobs;
    currentView.value = 'results';
    
  } catch (error) {
    console.error("Analysis failed:", error);
    alert("Analysis failed.");
    currentView.value = 'upload';
  }
};

const handleViewGroup = (group) => {
  selectedGroup.value = group;
  currentView.value = 'groupDetail';
};

const handleBackToResults = () => {
  currentView.value = 'results';
  selectedGroup.value = null;
};
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
        @confirm="alert('Deletions Confirmed (Mock)')"
        @view-group="handleViewGroup"
      />
    </template>

    <!-- Group Detail View -->
    <template v-else-if="currentView === 'groupDetail'">
      <GroupDetailView
        :group="selectedGroup"
        @back="handleBackToResults"
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
  margin-top: auto; /* Push to bottom of content area */
  margin-bottom: 24px;
  padding: 0 16px;
}
</style>
