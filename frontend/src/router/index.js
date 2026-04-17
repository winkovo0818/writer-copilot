import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    redirect: '/editor',
    children: [
      {
        path: 'editor',
        name: 'editor',
        component: () => import('@/views/Editor.vue'),
        meta: { title: '创作工作台' },
      },
      {
        path: 'knowledge',
        name: 'knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识库' },
      },
      {
        path: 'graph',
        name: 'graph',
        component: () => import('@/views/Graph.vue'),
        meta: { title: '知识图谱' },
      },
      {
        path: 'style',
        name: 'style',
        component: () => import('@/views/StyleReport.vue'),
        meta: { title: '风格报告' },
      },
      {
        path: 'matrix',
        name: 'matrix',
        component: () => import('@/views/Matrix.vue'),
        meta: { title: '内容矩阵' },
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据看板' },
      },
      {
        path: 'llm',
        name: 'llm',
        component: () => import('@/views/LlmMonitor.vue'),
        meta: { title: 'LLM 监控' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} — Creator Copilot`
  }
})

export default router
