import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

export default {
  state() {
    return {
      userId: null,
      token: null,
      name: null,
    }
  },
  getters: {
    userId(state) {
      return state.userId;
    },
    token(state) {
      return state.token;
    },
    isAuthenticated(state) {
      return !!state.token;
    },
    userAuthUrl(_, getters) {
      return 'http://' + getters.url + '/api/user/token/';
    },
    checkMeUrl(_, getters) {
      return 'http://' + getters.url + '/api/user/me/';
    },
    headers(state) {
      return { Authorization: `Token ${state.token}` }
    }
  },
  mutations: {
    setUser(state, payload) {
      state.token = payload.token;
      state.userId = payload.userId;
      state.name = payload.userName;
    },
  },
  actions: {
    async auth(context, payload) {
      try {
        const response = await axios.post(context.getters['userAuthUrl'], payload);

        const whoami = await axios.get(context.getters['checkMeUrl'], { headers: { Authorization: `Token ${response.data.token}` } });

        localStorage.setItem('token', response.data.token);
        localStorage.setItem('userId', whoami.data.email);
        localStorage.setItem('name', whoami.data.name);

        context.commit('setUser', {
          token: response.data.token,
          userId: whoami.data.email,
          name: whoami.data.name,
        })
      } catch(error) {
        console.log(error)
        const newError = new Error(error.message || 'Failed to authenticate.');
        throw newError
      }
    },
    autoLogin(context) {
      const token = localStorage.getItem('token');
      const userId = localStorage.getItem('userId');
      const name = localStorage.getItem('name');

      if (token && userId) {
        context.commit('setUser',{
          token: token,
          userId: userId,
          name: name,
        });
      }
    },
    async login(context, payload) {
      return context.dispatch('auth', {
        ...payload,
      });
    },
    logout(context) {
      localStorage.removeItem('token');
      localStorage.removeItem('userId');
      localStorage.removeItem('name');

      context.commit('setUser', {
        token: null,
        userId: null,
        name: null,
      })
    }
  },
}