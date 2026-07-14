import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', name: 'events', component: () => import('../views/EventList.vue') },
  { path: '/events/:id', name: 'event-detail', component: () => import('../views/EventDetail.vue'), props: true },
  { path: '/events/new', name: 'event-new', component: () => import('../views/EventForm.vue'), meta: { requiresOfficer: true } },
  { path: '/events/:id/edit', name: 'event-edit', component: () => import('../views/EventForm.vue'), props: true, meta: { requiresOfficer: true } },

  { path: '/organizations', name: 'organizations', component: () => import('../views/OrgList.vue') },
  { path: '/organizations/:id', name: 'org-profile', component: () => import('../views/OrgProfile.vue'), props: true },
  { path: '/organizations/:id/edit', name: 'org-edit', component: () => import('../views/OrgForm.vue'), props: true, meta: { requiresOfficer: true } },
  { path: '/users', name: 'users', component: () => import('../views/UserManagement.vue'), meta: { requiresOfficer: true } },

  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { guestOnly: true } },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue'), meta: { guestOnly: true } },

  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresOfficer && auth.role !== 'officer' && auth.role !== 'admin') {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
