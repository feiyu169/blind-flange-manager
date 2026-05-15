import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'blind-flanges',
        name: 'BlindFlangeList',
        component: () => import('../views/blind-flange/List.vue'),
      },
      {
        path: 'blind-flanges/:id',
        name: 'BlindFlangeDetail',
        component: () => import('../views/blind-flange/Detail.vue'),
      },
      {
        path: 'workflows',
        name: 'WorkflowList',
        component: () => import('../views/workflow/List.vue'),
      },
      {
        path: 'inventory',
        name: 'InventoryList',
        component: () => import('../views/inventory/List.vue'),
      },
      {
        path: 'inspections',
        name: 'InspectionList',
        component: () => import('../views/inspection/List.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
