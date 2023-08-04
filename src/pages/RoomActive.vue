<template>
  <section>
    <div class="container">
      <div class="score">
        <ul>
          <li v-for="score in scores" :key="score">{{ score }}</li>
        </ul>
        <p class="bottom">{{ readyTotal }}</p>
        <p class="progress">{{ progress }}</p>
      </div>
      <div class="hint">
        <p>{{ dHint }}</p>
        <p>{{ sHint }}</p>
        <p class="thint">{{ tHint }}</p>
        <p class="bottom">{{ timer }}초</p>
      </div>
    </div>
    <div>
      <transition name="thumnail">
        <img :src="imgsrc" v-if="showAnswer && imgsrc">
      </transition>
      <textarea readonly ref="chatRecord" @input="resize" :value="textValue"></textarea>
    </div>
    <div>
      <input type="text" @keypress.enter="submit" v-model.trim="enteredInput"/>
      <button @click="submit">Send</button>
      <button @click="skip">Skip</button>
    </div>
  </section>
</template>

<script>
import JSConfetti from 'js-confetti';

export default {
  data() {
    return {
      enteredInput: '',
      unmount: false,
      error: null,
      reconnectInterval: null,
      tHint: '',
      sHint: '',
      dHint: '',
      titleHint: '',
      titleLength: 0,
      singer: '',
      description: '',
      imgsrc: '',
      confetti: new JSConfetti(),
      cho: ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"],
      dTm: 20,
      sTm: 40,
      tTm: 70,
      tItv: 15,
      keyPressSound: null,
    };
  },
  watch: {
    textValue() {
      const textarea = this.$refs.chatRecord;
      if (textarea) {
        textarea.scrollTop = textarea.scrollHeight;
      }
    },
    timer(value) {
      if (!this.showAnswer) {
        if (value === this.dTm) {
        this.dHint = this.description;
        }
        if (value === this.sTm) {
          this.sHint = this.singer;
        }
        if ( value>=this.tTm && Math.floor((value-this.tTm)/this.tItv) <= this.titleLength && value%this.tItv === 0) {
          this.tHint = this.titleHint.slice(0, Math.floor((value-this.tTm)/this.tItv))
          const last = Math.floor((value-this.tTm)/this.tItv);
          for (const c of this.titleHint.slice(last,this.titleLength).split(' ')) {
            this.tHint += '＿'.repeat(c.length) + ' ';
          }
          this.tHint.trim();
        }
      }
    },
    currSongInfo(value) {
      this.tHint = '';
      this.sHint = '';
      this.dHint = '';
      this.titleHint = '';
      this.imgsrc = '';
      this.titleLength = value['title'].length;
      for ( const i in value['title'] ) {
        const code = value['title'].charCodeAt(i);
        if (code>44031 && code<55204) {
          this.titleHint += this.cho[Math.floor((+code-44032)/588)];
        } else if(code>47 && code<58) {
          this.titleHint += '0';
        } else if(code === 32) {
          this.titleHint += ' ';
        } else if(code>64 && code<91 || code>96 && code<123) {
          this.titleHint += 'a';
        } else {
          this.titleHint += '*';
        }
      }
      this.imgsrc = value['image']
      this.singer = value['singer'];
      this.description = value['description'];
    },
    isCorrect(value) {
      if (value) {
        this.confetti.addConfetti();
      }
    },
    showAnswer(value) {
      if (value && this.currSongInfo) {
        this.tHint = this.currSongInfo['title'];
        this.sHint = this.currSongInfo['singer'];
        this.dHint = this.currSongInfo['description'];
      }
    }
  },
  computed: {
    isSkipped() {
      return this.$store.getters['room/getIsSkipped'] || this.showAnswer;
    },
    progress() {
      return 'ROUND ' + this.$store.getters['room/getProgress'];
    },
    isCorrect() {
      return this.$store.getters['room/getCorrect'];
    },
    showAnswer() {
      return this.$store.getters['room/getShowAnswer'];
    },
    currSongInfo() {
      return this.$store.getters['room/getCurrSongInfo'];
    },
    timer() {
      return this.$store.getters['room/getTimer'];
    },
    textValue() {
      return this.$store.getters['room/getTextRecord'].join('\n');
    },
    socket() {
      return this.$store.getters['room/getSocket'];
    },
    currAudio() {
      return this.$store.getters['room/getCurrAudio'];
    },
    scores() {
      return this.$store.getters['room/getScore'];
    },
    readyTotal() {
      return this.$store.getters['room/getReadyTotal'];
    },
  },
  methods: {
    submit() {
      if (this.enteredInput) {
        this.socket.send(JSON.stringify({
        'message': this.enteredInput
      }))
      }
      this.enteredInput = '';
    },
    skip() {
      if (!this.isSkipped) {
        this.keyPressSound.play();
      }
      this.socket.send(JSON.stringify({
        'action': 'skip'
      }))
    },
    async access() {
      this.error = null;
      try {
        await this.$store.dispatch('room/accessRoom',{
        name: this.$store.getters['room/getRoomName'],
        password: this.$store.getters['room/getRoomPass'],
        mode: 'access',
      })
      } catch(error) {
        this.error = error.message || 'Something went wrong!';
        console.log(this.error);
      }
    },
    leave(event) {
      event.preventDefault();
      event.returnValue = '';
    },
    skipKeyDown(event) {
      if ( event.target.nodeName == 'INPUT' ) return;
      if ( event.key.toLowerCase() === 'p' && !this.isSkipped ) {
        this.skip();
      }
    }
  },
  mounted() {
    window.addEventListener("keydown", this.skipKeyDown);
    window.addEventListener('beforeunload', this.leave);
    this.reconnectInterval = setInterval(() => {
      if (this.socket && !this.unmount && this.socket.readyState == 3) {
        console.log('try reconnect...')
        this.access();
      }
    }, 2000);
    this.keyPressSound = new Audio(require('./sound/skip.mp3'));
  },
  beforeUnmount() {
    console.log('before-unmount')
    window.removeEventListener("keydown", this.skipKeyDown);
    window.removeEventListener('beforeunload', this.leave)
    this.unmount = true;
    clearInterval(this.reconnectInterval)
    this.$store.commit('room/clearCron')
    this.$store.commit('room/initData')
    // this.$router.replace('/home');
  },
}
</script>

<style scoped>

.thumnail-enter-from {
  opacity: 0;
  transform: translate(-100%, -50%);
}
.thumnail-enter-active {
  transition: all 0.6s ease-in;
}
.thumnail-leave-from,
.thumnail-enter-to {
  opacity: 0.3;
  transform: translate(-50%, -50%);
}
.thumnail-leave-active {
  transition: all 0.6s ease-out;
}

.thumnail-leave-to {
  opacity: 0;
  transform: translate(0%, -50%);
}

section {
  text-align: center;
}
div {
  position: relative;
  text-align: center;
  margin: 5px;
}
.score {
  display: inline-block;
  text-align: left;
  margin: 0;
  border: solid 1px white;
  height: 200px;
  max-width: 50%;
  width: 320px;
}
.hint {
  display: inline-block;
  text-align: center;
  margin: 0;
  border: solid 1px white;
  height: 200px;
  max-width: 50%;
  width: 320px;
}
textarea {
  max-width: 100%;
  width: 640px;
  height: 360px;
  border: none;
  color: white;
  opacity: 1;
  overflow: hidden;
  background-color: rgb(0,0,0,0);
}
.thint {
  letter-spacing: 2px;
}
img {
  display: inline-block;
  position: absolute;
  width: 360px;
  height: 360px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.3;
}
.container {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.bottom {
  position: absolute;
  bottom: 0;
  margin-left: 10px;
}

.progress {
  position: absolute;
  bottom: 0;
  right: 0;
  margin-right: 10px;
}

input {
  max-width: 500px;
  width: 70%;
  height: 32px;
  border: solid 1px white;
  outline: none;
  padding-left: 5px;
  color: white;
  background-color:rgb(0,0,0,0);
}

button {
  background-color: rgb(0,0,0,0);
  border: solid 1px white;
  max-width: 60px;
  width: 12%;
  height: 32px;
  margin-left: 10px;
  color: white;
}

ul {
  list-style: none;
  padding-left: 10px;
  font-size: 15px;
}


</style>