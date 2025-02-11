import { createRouter, createWebHistory } from 'vue-router'
import DocumentList from '../components/DocumentList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'DocumentList',
      component: DocumentList,
    },
  ],
})

export default router
