import { createStore } from 'vuex';

import authModule from './modules/auth.js';
import roomModule from './modules/room.js';
import musicModule from './modules/music.js';

const store = createStore({
  modules: {
    auth: authModule,
    room: roomModule,
    music: musicModule,
  },
  state() {
    return {
      url: process.env.VUE_APP_API_URL,
    };
  },
  getters: {
    url(state) {
      return state.url;
    },
  }
})

export default store;
