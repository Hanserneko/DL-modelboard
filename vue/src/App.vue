<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue'
import app from './components/app.vue'

</script>

<template>
  <app />
</template>


<style>
html,
body,
#app {
  width: 100vw;
  height: 100vh;
  margin: 0 0;
  padding: 0 0;
  box-sizing: border-box;
}
</style>
