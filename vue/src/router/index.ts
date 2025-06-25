import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/model',
      name: 'model',
      component: () => import('../views/ModelView.vue'),
    },
    {
      path: '/dataset',
      name: 'dataset',
      component: () => import('../views/DatasetView.vue'),
    },
    {
      path: '/task',
      name: 'task',
      component: () => import('../views/TaskView.vue'),
    },
    {
      path: '/setting',
      name: 'setting',
      component: () => import('../views/SettingView.vue'),
    },
  ],
})

export default router
