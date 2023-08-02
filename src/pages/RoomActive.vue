<template>
  <section>
    <div class="container">
      <div class="score">
        <ul>
          <li v-for="score in scores" :key="score">{{ score }}</li>
        </ul>
        <p class="bottom">{{ readyTotal }}</p>
      </div>
      <div class="hint">
        <p>{{ dHint }}</p>
        <p>{{ sHint }}</p>
        <p class="thint">{{ tHint }}</p>
        <p class="bottom">{{ timer }}초</p>
      </div>
    </div>
    <div>
      <transition name="music">
        <img :src="imgsrc" v-if="isCorrect">
      </transition>
      <textarea readonly ref="chatRecord" @input="resize" :value="textValue"></textarea>
    </div>
    <div>
      <input type="text" @keypress.enter="submit" v-model.trim="enteredInput"/>
      <button @click="submit">Submit</button>
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
      cho: ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"],
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
      if (!this.isCorrect) {
        if (value === 30) {
        this.dHint = this.description;
        }
        if (value === 60) {
          this.sHint = this.singer;
        }
        if ( value>=90 && Math.floor((value-90)/10) <= this.titleLength && value%10 === 0) {
          this.tHint = this.titleHint.slice(0,Math.floor((value-90)/10))
          let last = Math.floor((value-90)/10);
          if (this.titleHint[last] === ' ') {
            this.tHint += ' ';
            last += 1;
          }
          for (const c of this.titleHint.slice(last,this.titleLength)) {
            this.tHint += '_'.repeat(c.length)+' ';
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
        let code = value['title'].charCodeAt(i);
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
      const resizedImage = value['image'].split('=');
      resizedImage.pop();
      this.imgsrc = resizedImage.join('=')+'=w544-h544-l90-rj'
      this.singer = value['singer'];
      this.description = value['description'];
    },
    isCorrect(value) {
      if (value) {
        const confetti = new JSConfetti();
        confetti.addConfetti();
        this.tHint = this.currSongInfo['title'];
        this.sHint = this.currSongInfo['singer'];
        this.dHint = this.currSongInfo['description'];
      }
    }
  },
  computed: {
    isCorrect() {
      return this.$store.getters['room/getCorrect'];
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
      this.socket.send(JSON.stringify({
        'message': this.enteredInput
      }))
      this.enteredInput = '';
    },
    skip() {
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
    }
  },
  beforeUnmount() {
    console.log('before-unmount')
    this.unmount = true;
    clearInterval(this.reconnectInterval)
    this.$store.commit('room/initData')
    this.$router.replace('/home');
  },
  mounted() {
    this.reconnectInterval = setInterval(() => {
      if (this.socket && !this.unmount && this.socket.readyState == 3) {
        console.log('try reconnect...')
        this.access();
      }
    }, 2000);
  }
}
</script>

<style scoped>

.music-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.music-enter-active {
  transition: all 5s ease-in;
}
.music-enter-to {
  opacity: 0.3;
  transform: translateY(0);
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
  width: 320px;
}
.hint {
  display: inline-block;
  text-align: center;
  margin: 0;
  border: solid 1px white;
  height: 200px;
  width: 320px;
}
.thint {
  letter-spacing: 5px;
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
  margin: 0;
}

.bottom {
  position: absolute;
  bottom: 0;
  margin-left: 10px;
}

input {
  width: 500px;
  height: 32px;
  border: solid 1px white;
  outline: none;
  padding-left: 10px;
  color: white;
  background-color:rgb(0,0,0,0);
}

button {
  background-color: rgb(0,0,0,0);
  border: solid 1px white;
  height: 32px;
  margin-left: 10px;
  color: white;
}

textarea {
  width: 640px;
  height: 360px;
  border: solid 1px white;
  color: white;
  opacity: 1;
  overflow: hidden;
  background-color: rgb(0,0,0,0);
}

ul {
  list-style: none;
  padding-left: 10px;
  font-size: 15px;
}


</style>