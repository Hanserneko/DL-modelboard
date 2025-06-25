<template>
  <div class="task-view">
    <main>
      <TaskPanel />
    </main>
  </div>
</template>

<script setup lang="ts">
import TaskPanel from '../components/TaskPanel.vue'
</script>

<style scoped>
.task-view {
  padding: 24px;
}
</style>
