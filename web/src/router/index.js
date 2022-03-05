import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Jobs',
    component: () => import(/* webpackChunkName: "about" */ '../views/Jobs.vue')
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: () => import(/* webpackChunkName: "about" */ '../views/Jobs.vue')
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import(/* webpackChunkName: "about" */ '../views/Devices.vue')
  },
  {
    path: '/providers',
    name: 'Providers',
    component: () => import(/* webpackChunkName: "about" */ '../views/Providers.vue')
  },
  {
    path: '/account',
    name: 'Account',
    component: () => import(/* webpackChunkName: "about" */ '../views/Account.vue')
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
