import { createStore } from 'vuex';

import authModule from './modules/auth.js';
import roomModule from './modules/room.js';

const store = createStore({
  modules: {
    auth: authModule,
    room: roomModule,
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
