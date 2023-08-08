<template>
  <section>
    <base-dialog :show="!!error" @close="closeError">{{ error }}</base-dialog>
    <section class="result-box">
      <base-spinner v-if="isLoading"></base-spinner>
      <div class="search-result" v-else>
        <div class="image-block">
          <a :href="link" target="_blank"> <!--v-if="image"-->
            <img :src="image" class="thumbnail">
            <img src="@/pages/image/link.png" class="link-img">
          </a>
        </div>
        <div class="music-info">
          <span v-if="image && windowState>0"> <!---->
            <h3>{{ searchResult.title }}</h3>
            <h4>{{ searchResult.singer }}</h4>
          </span>
          <p class="instruction">{{ instruction }}</p>
        </div>
      </div>
    </section>
    <form @submit.prevent="submit">
      <div class="form-control">
        <label for="title">Title</label>
        <input id="title" type="text" v-model.trim="title"/>
      </div>
      <div class="form-control">
        <label for="singer">Singer</label>
        <input id="singer" type="text" v-model.trim="singer"/>
      </div>
      <div class="form-control" v-if="windowState>0 && windowState!==2">
        <label for="description">Description</label>
        <input id="description" type="text" v-model.trim="description"/>
      </div>
      <div class="form-control" v-if="windowState>0 && windowState!==2">
        <label>Tags</label>
        <ul>
          <li v-for="(value, name) of tagList" :key="name">
            <button
            type="button"
            @click="selectTag"
            :value="value"
            class="tag-button"
            :class="{active: value===tag}"
            >{{ value }}</button>
          </li>
        </ul>
      </div>
      <base-button v-if="windowState!==3">{{ formButtonName }}</base-button>
      <base-button type="button" @click="clear">Clear</base-button>
    </form>
  </section>
</template>

<script>
export default {
  data() {
    return {
      title: '',
      singer: '',
      link: '',
      description: '',
      tag: '',
      image: '',
      instruction: '',
      error: null,
      isLoading: false,
    }
  },
  watch: {
    windowState(value) {
      if (value===1) {
        this.instruction = 'Add tag and register music.';
      } else if (value===2) {
        this.instruction = 'This song already exists.';
      } else if (value===3) {
        this.instruction = 'Register Success';
      } else if (value===4) {
        this.instruction = 'Register Fail';
      } else {
        this.instruction = '';
      }
    }
  },
  computed: {
    tagList() {
      return this.$store.getters['music/getTagGenre'];
    },
    searchState() {
      return this.$store.getters['music/getSearchState'];
    },
    registerState() {
       return this.$store.getters['music/getRegisterState'];
    },
    formButtonName() {
      return this.windowState!==0 && this.windowState!==2 ? 'Register':'Search';
    },
    isExist() {
      return this.$store.getters['music/isExist']
    },
    searchResult() {
      return this.$store.getters['music/searchResult']
    },
    windowState() {
      if (!this.searchState) {
        return 0; //before search
      } else if (!this.registerState && !this.isExist) {
        return 1; //not exist
      } else if (!this.registerState && this.isExist) {
        return 2; //already exist
      } else if (this.registerState===1) {
        return 3; //register success
      } else {
        return 4; //register fail
      }
    }
  },
  methods: {
    async submit() {
      if (!this.title) {
        this.error = 'Please enter the title.';
        return;
      }
      if (this.windowState===2) {
        this.$store.commit('music/clearData');
      }
      this.isLoading = true;
      if (!this.searchState) {
        try {
          await this.$store.dispatch('music/searchMusic',{
          title: this.title,
          singer: this.singer
        })
          if (!this.isExist) {
            this.title = this.searchResult.title;
            this.singer = this.searchResult.singer;
          } else {
            this.title = '';
            this.singer = '';
          }
          console.log(this.isExist)
          console.log(this.title)
          this.link = 'https://www.youtube.com/watch?v=' + this.searchResult.id;
          this.image = this.searchResult.image + '=w150-h150-l90-rj';
        } catch(error) {
          this.error = error.message || 'Something went wrong.'
        }
      } else if (this.registerState!==2) {
        if (!this.tag) {
          this.error = 'Please select tag.';
          return;
        }
        try {
          await this.$store.dispatch('music/registerMusic',{
            title: this.title,
            singer: this.singer,
            tags: [{
              name: this.tag
            }],
            description: this.description,
        })
        } catch(error) {
          this.error = 'Download Fail!';
        }
      }
      this.isLoading = false;
      console.log(this.registerState)
      console.log(this.searchState)
      console.log(this.isExist)
    },
    selectTag(event) {
      if (this.tag === event.target.value) {
        this.tag = '';
      } else {
        this.tag = event.target.value;
      }
    },
    clear() {
      this.title = '';
      this.singer = '';
      this.image = '';
      this.desription = '';
      this.tag = '';
      this.error = null;
      this.instruction = '';
      this.$store.commit('music/clearData');
    },
    keyDown(event) {
      if ( event.keyCode == 13 && this.windowState!==3 ) {
        this.submit();
      }
      if ( event.keyCode == 27 && !!this.error ) {
        this.closeError();
      }
      if ( event.keyCode == 27 && !this.error ) {
        this.clear();
      }
    },
    closeError() {
      this.error = null;
    }
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
  },
  beforeUnmount() {
    window.removeEventListener("keydown", this.keyDown);
    this.clear();
  }
}
</script>

<style scoped>

form {
  padding: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  margin: auto;
  width: 100%;
  max-width: 420px;
}

input {
  display: block;
  font: inherit;
  padding: 0.15rem;
  margin-top: 1rem;
  height: 30px;
  width: 95%;
}

.form-control {
  margin: 0.5rem 0;
  flex-basis: 50%;
  height: 75px;
  box-sizing: border-box;
  border: 1px solid black;
}

ul {
  display: flex;
  flex-wrap: wrap;
  list-style-type: none;
  padding: 0;
}
li {
  position: relative;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 15px;
  height: 30px;
  width: 75px;
  margin: 0.5rem;
}

.tag-button {
  background-color: rgba(255,255,255,0.1);
  border: none;
  color: white;
  white-space: nowrap;
  height: inherit;
  width: inherit;
  border-radius: 10px;
}
.active {
  border: white 1px solid;
}

.search-result {
  display: flex;
  justify-content: center;
  height: inherit;
}
.result-box {
  height: 150px;
  max-width: 400px;
  border: solid 1px rgba(255,255,255,0.1);
  margin: auto;
}
.music-info {
  font: inherit;
  width: 250px;
  position: relative;
  margin-left: 0.5rem;
}

.instruction {
  position: absolute;
  bottom: 0;
  right: 1rem;
  color: red;
  font-size: 13px;
}

span {
  white-space: nowrap;
}

img {
  position: absolute;
}
.image-block {
  position: relative;
  display: inline-block;
  height: 150px;
  width: 150px;
}
.link-img {
  opacity: 0;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

a:hover {
  cursor: pointer;
}
a:hover .thumbnail {
  opacity: 0.3;
}

a:hover .link-img {
  opacity: 0.9;
}
</style>