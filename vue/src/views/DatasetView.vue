<template>
  <div class="dataset-view">

    <main>
      <DatasetPanel />
    </main>
  </div>
</template>

<script setup lang="ts">
import DatasetPanel from '../components/DatasetPanel.vue'
</script>

<style scoped>
.dataset-view {
  padding: 24px;
}
</style>
