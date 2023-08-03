import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

export default {
  namespaced: true,
  state() {
    return {
      roomName: '',
      password: '',
      correct: false,
      showAnswer: false,
      cron: null,
      currAudio: null,
      chatSocket: null,
      timer: 0,
      currSongIndex: -1,
      musicLength: 0,
      roomReadyNum: 0,
      roomTotalNum: null,
      score: null,
      playList: [],
      textRecord: [],
    };
  },
  getters: {
    getProgress(state) {
      return state.currSongIndex+1+' / '+state.musicLength;
    },
    getTextRecord(state) {
      return state.textRecord;
    },
    getRoomName(state) {
      return state.roomName;
    },
    getRoomPass(state) {
      return state.password;
    },
    getCurrAudio(state) {
      return state.currAudio;
    },
    getCorrect(state) {
      return state.correct;
    },
    getShowAnswer(state) {
      return state.showAnswer;
    },
    getTimer(state) {
      return state.timer;
    },
    getScore(state) {
      return state.score;
    },
    getReadyTotal(state) {
      return 'SKIP ' + state.roomReadyNum + ' / ' + state.roomTotalNum;
    },
    getSocket(state) {
      return state.chatSocket;
    },
    apiUrl(_, _2 ,_3 ,rootGetters) {
      return 'http://' + rootGetters.url + '/api/music/rooms/'
    },
    musicUrl(_, _2, _3, rootGetters) {
      return 'http://' + rootGetters.url + '/api/music/musics/'
    },
    socketUrl(state, _2, _3, rootGetters) {
      return 'ws://' + rootGetters.url + `/ws/chat/${state.roomName}/?token=${rootGetters.token}`
    },
    getSocketReadyState(state) {
      if (state.chatSocket) {
        return state.chatSocket.readyState;
      }
      return null;
    },
    getCurrSongInfo(state) {
      if (state.currSongIndex >= 0 && state.currSongIndex < state.playList.length) {
        return {
          title: state.playList[state.currSongIndex]['title'],
          singer: state.playList[state.currSongIndex]['singers'][0]['name'],
          description: state.playList[state.currSongIndex]['description'],
          image: state.playList[state.currSongIndex]['image'],
        }
      }
      return null;
    },
  },
  mutations: {
    setCorrect(state, payload) {
      state.correct = payload['correct'];
    },
    setShowAnswer(state, payload) {
      state.showAnswer = payload['showAnswer'];
    },
    setScore(state, payload) {
      state.score = payload['score'];
    },
    setSocket(state, payload) {
      state.chatSocket = new WebSocket(payload['url']);
    },
    setPlayList(state, payload) {
      state.playList = payload['playList'];
    },
    setRoomInfo(state, payload) {
      // state.chatSocket = payload['chatSocket'];
      state.roomName = payload['roomName'];
      state.password = payload['password'];
      state.musicLength = payload['length'];
    },
    setNum(state, payload) {
      if ('ready' in payload) {
        state.roomReadyNum = payload['ready'];
      }
      if ('total' in payload) {
        state.roomTotalNum = payload['total'];
      }
    },
    appendText(state, payload) {
      if (state.textRecord.length > 22) {
        state.textRecord.shift();
      }
      state.textRecord.push(payload['message']);
    },
    setRound(state, payload) {
      state.currSongIndex = +payload['round'];
    },
    clearCron(state) {
      if (state.currAudio !== null) {
        clearInterval(state.cron);
        state.correct = false;
        state.showAnswer = false;
        state.timer = 0;
        state.currAudio.pause();
      }
    },
    setAudio(state) {
      state.currAudio = new Audio(state.playList[state.currSongIndex]['audio']);
      state.currAudio.addEventListener('ended', () => {
        state.chatSocket.send(JSON.stringify({
          'action': 'skip'
        }))
      });
      state.cron = setInterval(() => {
        state.timer++;
       }, 1000)
      state.currAudio.play()
    },
    initData(state) {
      // clearCron needed
      if (state.chatSocket && state.chatSocket.readyState !== 3) {
        state.chatSocket.close()
      }
      state.cron= null;
      state.currSongIndex= -1;
      state.currAudio= null;
      state.chatSocket= null;
      state.roomName= '';
      state.password= '';
      state.playList= [];
      state.textRecord= [];
      state.roomTotalNum= null;
      state.roomReadyNum= 0;
      state.musicLength= 0;
      state.score= null;
    },
  },
  actions: {
    async accessRoom(context, payload) {
      try {
        const response = payload['mode'] === 'access'? await axios.get(context.getters.apiUrl + `${payload['name']}/`, {
          params: { password: payload['password'] },
          headers: context.rootGetters['headers']
        }):await axios.post(context.getters.apiUrl,
          { name: payload['name'], password: payload['password'], music_length: payload['length'] },
          { headers: context.rootGetters['headers'] });

        context.commit('setRoomInfo', {
          roomName: response.data['name'],
          password: response.data['password'],
          length: response.data['music_length']
        })

        context.commit('setSocket', { url: context.getters['socketUrl']});
        const socket = context.getters['getSocket'];

        socket.onmessage = (event) => {context.dispatch('onMessage', JSON.parse(event.data))};
        socket.onopen = () => { context.dispatch('onOpen', {'music_list': response.data['music_list']}) }
        // socket.onclose = () => { context.commit('initData') };

      } catch(error) {
        const newError = new Error(error.message || 'Access denied');
        throw newError
      }
    },
    async onOpen(context, payload) {
      try {
        const music_list = payload['music_list'].join(',');

        const music_info = await axios.get(context.getters['musicUrl']+`?musics=${encodeURIComponent(music_list)}`, { headers: context.rootGetters['headers'] });

        context.commit('setPlayList',{ 'playList': music_info.data });
      } catch(error) {
        const newError = new Error(error.message || 'Access denied');
        throw newError
      }
    },
    onMessage(context, payload) {
      if ('message' in payload) {
        context.commit('appendText',{ 'message': payload['user_name'] + ': ' + payload['message'] })
      } else if ('action' in payload) {
        if ('round' in payload) {
          context.commit('setRound', payload);
          if (payload['action'] == 'start') {
            context.commit('setAudio');
          } else if (payload['action'] == 'skip') {
            context.commit('clearCron');
            context.commit('setAudio');
          } else {
            context.commit('clearCron');
          }
          context.commit('setNum', { 'ready': 0 });
        } else if (payload['action'] === 'correct') {
          context.commit('appendText',{
            'message': '정답 ' + payload['user_name'],
          })
          context.commit('setCorrect', {'correct':true});
          context.commit('setShowAnswer', {'showAnswer':true});
        } else if (payload['action'] === 'showAnswer') {
          context.commit('setShowAnswer', {'showAnswer':true});
        }
      } else if ('ready' in payload) {
        context.commit('setNum', payload)
      } else if ('notice' in payload) {
        context.commit('appendText',{
          'message': payload['user_name']+'님이 '+ (payload['notice'] === 'enter'? '입장':'퇴장') +'하였습니다.',
        })
        context.commit('setNum', { 'total': payload['total'] })
      } else if ('score' in payload) {
        const score = []
        const name_list = payload['user_names'].slice(0,-1).split(',');
        const score_list = payload['score'].slice(0,-1).split(',');
        for (const i in name_list) {
          score.push(`${+i+1}등 ${name_list[i]} ${score_list[i]}점`)
        }
        context.commit('setScore', { 'score': score })
      }
    },
  }
}

