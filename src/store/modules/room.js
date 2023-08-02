import axios from 'axios';

export default {
  namespaced: true,
  state() {
    return {
      cron: null,
      timer: 0,
      currSongIndex: -1,
      currAudio: null,
      chatSocket: null,
      roomName: '',
      password: '',
      playList: [],
      textRecord: [],
      correct: false,
      roomTotalNum: null,
      roomReadyNum: 0,
      score: null,
    };
  },
  getters: {
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
    getTimer(state) {
      return state.timer;
    },
    getScore(state) {
      return state.score;
    },
    getReadyTotal(state) {
      return 'SKIP ' + state.roomReadyNum + ' / ' + state.roomTotalNum;
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
    getSocket(state) {
      return state.chatSocket;
    },
    getSocketReadyState(state) {
      if (state.chatSocket) {
        return state.chatSocket.readyState;
      }
      return null;
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
    }
  },
  mutations: {
    setCorrect(state, payload) {
      state.correct = payload['correct'];
    },
    clearCron(state) {
      clearInterval(state.cron);
      state.timer=0;
    },
    initData(state) {
      if (state.cron) {
        clearInterval(state.cron)
      }
      if (state.currAudio) {
        state.currAudio.pause()
      }
      if (state.chatSocket && state.chatSocket.readyState !== 3) {
        state.chatSocket.close()
      }
      state.cron= null;
      state.timer= 0;
      state.currSongIndex= -1;
      state.currAudio= null;
      state.chatSocket= null;
      state.roomName= '';
      state.password= '';
      state.playList= [];
      state.textRecord= [];
      state.correct= false;
      state.roomTotalNum= null;
      state.roomReadyNum= 0;
      state.score= null;
    },
    setRoomInfo(state, payload) {
      // state.chatSocket = payload['chatSocket'];
      state.roomName = payload['roomName'];
      state.password = payload['password'];
    },
    appendText(state, payload) {
      if (state.textRecord.length > 22) {
        state.textRecord.shift();
      }
      state.textRecord.push(payload['message']);
    },
    setSocket(state, payload) {
      state.chatSocket = new WebSocket(payload['url']);
    },
    setPlayList(state, payload) {
      state.playList = payload['playList'];
    },
    startGame(state, payload) {
      state.currSongIndex = +payload['round'];
      state.correct = false;
      state.currAudio = new Audio(state.playList[state.currSongIndex]['audio']);
      console.log(state.playList[state.currSongIndex])
      console.log(state.currSongIndex)
      console.log(state.playList.length)
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
    skipGame(state, payload) {
      state.currSongIndex = +payload['round'];
      if (state.currAudio !== null) {
        clearInterval(state.cron);
        state.correct = false;
        state.timer = 0;
        state.currAudio.pause();
      }
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
    endGame(state, payload) {
      state.currSongIndex = +payload['round'];
      if (state.currAudio !== null) {
        clearInterval(state.cron);
        state.correct = false;
        state.timer = 0;
        state.currAudio.pause();
      }
    },
    setNum(state, payload) {
      if ('ready' in payload) {
        state.roomReadyNum = payload['ready'];
      }
      if ('total' in payload) {
        state.roomTotalNum = payload['total'];
      }
    },
    setScore(state, payload) {
      state.score = payload['score'];
    }
  },
  actions: {
    async accessRoom(context, payload) {
      try {
        let response;

        if (payload['mode'] === 'access') {
          const apiUrl = context.getters.apiUrl + `${payload['name']}/`;
          response = await axios.get(apiUrl, {
            params: { password: payload['password'] },
            headers: context.rootGetters['headers']
          });
        } else {
          const apiUrl = context.getters.apiUrl;
          response = await axios.post(apiUrl,
            { name: payload['name'], password: payload['password'] },
            { headers: context.rootGetters['headers'] });
        }

        context.commit('setRoomInfo', {
          roomName: response.data['name'],
          password: response.data['password'],
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
      console.log(payload)
      if ('message' in payload) {
        context.commit('appendText',{ 'message': payload['user_name'] + ': ' + payload['message'] })
      } else if ('action' in payload) {
        if ('round' in payload) {
          if (payload['action'] == 'start') {
            context.commit('startGame',payload)
          } else if (payload['action'] == 'skip') {
            context.commit('skipGame',payload)
          } else {
            context.commit('endGame',payload)
          }
          context.commit('setNum', { 'ready': 0 });
        } else if (payload['action'] === 'correct') {
          context.commit('appendText',{
            'message': '정답 ' + payload['user_name'],
          })
          context.commit('setCorrect', {'correct':true});
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
          console.log(typeof i)
          score.push(`${+i+1}등 ${name_list[i]} ${score_list[i]}점`)
        }
        context.commit('setScore', { 'score': score })
        console.log(score)
      }
    },
  }
}

