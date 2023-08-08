import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

export default {
  namespaced: true,
  state() {
    return {
      id: '',
      title: '',
      singer: '',
      image: '',
      year: '',
      time: '',
      tags: '',
      audio: null,
      searchState: false,
      registerState: 0,
      tagList: {
        2: "1990년대", 3: "2000년대", 4: "2010년대", 5: "2020년대",
        6: "발라드", 7: "댄스", 8: "랩/힙합", 9: "R&B/Soul", 10: "인디음악",
        11: "록/메탈", 12: "POP", 13: "포크/블루스", 14: "트로트"
      },
    }
  },
  getters: {
    getTagList(state) {
      return state.tagList;
    },
    getTagGenre(state) {
      return Object.fromEntries(Object.entries(state.tagList).filter(([key]) => key>5));
    },
    searchUrl(_, _2, _3, rootGetters) {
      return 'http://' + rootGetters.url + '/api/music/musics/search_music/'
    },
    registerUrl(_, _2, _3, rootGetters) {
      return 'http://' + rootGetters.url + '/api/music/musics/'
    },
    registerData(state) {
      return {
        id: state.id,
        title: state.title,
        singers: [{
          name: state.singer
        }],
        "running_time": state.time,
        "released_year": state.year,
        "image": state.image
      }
    },
    searchResult(state) {
      return {
        id: state.id,
        title: state.title,
        singer: state.singer,
        image: state.image
      }
    },
    getSearchState(state) {
      return state.searchState;
    },
    getRegisterState(state) {
      return state.registerState;
    },
    isExist(state) {
      return !!state.audio;
    }
  },
  mutations: {
    setRegisterState(state, payload) {
      state.registerState = payload['state'];
    },
    setMusicInfo(state, payload) {
      state.id = payload['id'];
      state.title = payload['title'];
      state.singer = payload['singers'][0]['name'];
      state.time = payload['running_time'];
      state.year = payload['released_year'];
      state.image = payload['image'];
      state.audio = payload['audio'];
      state.searchState = true;
    },
    clearData(state) {
      state.id = '';
      state.title = '';
      state.singer = '';
      state.image = '';
      state.year = '';
      state.time = '';
      state.tags = '';
      state.audio = null;
      state.searchState = false;
      state.registerState = 0;
    }
  },
  actions: {
    async searchMusic(context, payload) {
      try {
        const response = await axios.get(context.getters.searchUrl, {
          params: { 'title_singer': payload['title']+'--'+payload['singer'] },
          headers: context.rootGetters['headers']
        })
        console.log(response)
        context.commit('setMusicInfo', response.data);
      } catch(error) {
        const newError = new Error(error.message || 'Access denied');
        throw newError
      }
    },
    async registerMusic(context, payload) {
      try {
        const data = context.getters.registerData;
        if (payload['description']) {
          data.description = payload['description']
        }
        data.title = payload['title'];
        data.singer = payload['singer'];
        data.tags = payload['tags'];
        console.log(context.rootGetters['headers'])
        const response = await axios.post(context.getters.registerUrl, data,
          {headers: context.rootGetters['headers']}
        )
        console.log(response.data)
        context.commit('setRegisterState', { state : 1 })
      } catch(error) {
        const newError = new Error(error.message || 'Access denied');
        context.commit('clearData')
        throw newError
      }
    }
  }
}

