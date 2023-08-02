import { createRouter, createWebHistory } from 'vue-router';

import HomePage from './pages/HomePage.vue';
import NotFound from './NotFound.vue';
import store from './store/index.js'

const RoomActive = () => import('./pages/RoomActive.vue');
const UserAuth = () => import('./pages/UserAuth.vue');
const RoomCreate = () => import('./pages/RoomCreate.vue');
const RoomAccess = () => import('./pages/RoomAccess.vue');

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/home', component: HomePage },
    { path: '/auth', component: UserAuth, meta: { requiresUnauth: true } },
    { path: '/room/create', component: RoomCreate, meta: { requiresAuth: true } },
    { path: '/room/access', component: RoomAccess, meta: { requiresAuth: true } },
    { path: '/room/:roomId', component: RoomActive, meta: { requiresAuth: true, requiresRoomAuth: true } },
    { path: '/:notFound(.*)', component: NotFound },
  ]
})

router.beforeEach(function(to, _, next) {
  if ( to.meta.requiresAuth && !store.getters.isAuthenticated ) {
    next('/auth');
  } else if ( to.meta.requiresUnauth && store.getters.isAuthenticated ) {
    next('/home');
  } else if ( to.meta.requiresRoomAuth && store.getters['room/getRoomName'] != to.params.roomId ) {
    next('/room/access');
  } else {
    next();
  }
})

export default router;