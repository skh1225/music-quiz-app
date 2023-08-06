<template>
  <section v-if="!!this.socket">
    <div class="container">
      <div class="half">
        <ul>
          <li v-for="score in scores" :key="score">{{ score }}</li>
        </ul>
        <div class="bottom">
          <p>{{ readyTotal }}</p>
          <p>{{ progress }}</p>
        </div>
      </div>
      <div class="half" style="text-align:center">
        <p>{{ dHint }}</p>
        <p>{{ sHint }}</p>
        <p class="thint">{{ tHint }}</p>
        <div class="bottom">
          <p>{{ timer }}초</p>
        </div>
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
  <div v-else>
    <base-spinner></base-spinner>
  </div>
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
      dTm: 10,
      sTm: 15,
      tTm: 30,
      eta: 50,
      tLimit: 90,
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
        if  (value === this.tLimit) {
          this.socket.send(JSON.stringify({
            'action': 'skip'
          }))
        }
        if (value === this.dTm) {
        this.dHint = this.description;
        }
        if (value === this.sTm) {
          this.sHint = this.singer;
        }
        if ( value>=this.tTm && Math.floor((value-this.tTm)/this.tItv) <= this.titleLength && (value-this.tTm)%this.tItv === 0) {
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
    tItv() {
      return Math.floor(this.eta/this.titleLength)
    },
    isSkipped() {
      return this.$store.getters['room/getIsSkipped'];
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
      console.log(this.currSongInfo)
      console.log(this.$store.state['currSongIndex'])
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
      console.log(event)
      event.preventDefault();
      event.returnValue = '';
    },
    skipKeyDown(event) {
      if ( event.keyCode == 38 && !this.isSkipped ) {
        this.skip();
      }
    },
  },
  mounted() {
    console.log('mounted')
    window.addEventListener("keydown", this.skipKeyDown);
    window.addEventListener('beforeunload', this.leave);
    this.reconnectInterval = setInterval(() => {
      if (!this.unmount && !this.error && !this.socket) {
        console.log('try reconnect...')
        try {
          this.access();
        } catch(error) {
          this.error = error.message || 'Something went wrong!';
          console.log(this.error);
        }
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
.container {
  display: flex;
  flex-direction: row;
  justify-content: center;
  column-gap: 0.4rem;
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
  min-width: 360px;
}
.half {
  display: inline-block;
  text-align: left;
  margin: 0;
  border: none;
  background-color: rgba(255,255,255,0.1);
  height: 200px;
  max-width: 49%;
  width: 317px;
}
textarea {
  max-width: 100%;
  min-width: 360px;
  width: 640px;
  height: 360px;
  border: none;
  resize: none;
  opacity: 1;
  overflow: hidden;
  color: white;
  background-color: rgba(255,255,255,0.1);
}

textarea:focus {
  outline: none;
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

.bottom {
  bottom: 0;
  width: 100%;
  position: absolute;
  display: flex;
  justify-content: space-between;
  padding-right: 1rem;
  padding-left: 0.6rem;
  white-space: nowrap;
}

input {
  max-width: 500px;
  width: 70%;
  height: 32px;
  padding-left: 5px;
}

button {
  background-color: rgba(255,255,255,0.1);
  border: none;
  color: white;
  max-width: 60px;
  width: 12%;
  height: 32px;
  margin-left: 10px;
}

ul {
  list-style: none;
  padding-left: 10px;
}


</style>