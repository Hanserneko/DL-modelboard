import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/login': 'http://localhost:9982',
      '/register': 'http://localhost:9982',
      '/api/models': 'http://localhost:9982',
      '/api/upload_model': 'http://localhost:9982',
      '/api/delete_model': 'http://localhost:9982',
      '/api/tags': 'http://localhost:9982',
      '/api/add_tag': 'http://localhost:9982',
      '/api/datasets': 'http://localhost:9982',
      '/api/upload_dataset': 'http://localhost:9982',
      '/api/delete_dataset': 'http://localhost:9982',
    }
  }
})
