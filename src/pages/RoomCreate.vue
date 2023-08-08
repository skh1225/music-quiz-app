<template>
  <div>
    <base-dialog :show="!!error" @close="closeError">{{ error }}</base-dialog>
    <form @submit.prevent="access">
      <div class="form-control">
        <label for="roomName">Room Name</label>
        <input id="roomName" type="text" v-model.trim="roomName"/>
      </div>
      <div class="form-control">
        <label for="password">Password</label>
        <input id="password" type="password" v-model.trim="password"/>
      </div>
      <div class="form-control">
        <label for="round">Round</label>
        <input id="round" type="number" min="1" max="100" v-model.trim="round"/>
      </div>
      <div class="form-control">
        <label>Tags</label>
        <ul>
          <li v-for="(value, name) of tagList" :key="name">
            <button
            type="button"
            @click="toggleTag"
            :value="name"
            class="tag-button"
            :class="{active: tags[name]}"
            >{{ value }}</button>
          </li>
        </ul>
      </div>
      <base-button>Create</base-button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      roomName: '',
      password: '',
      tags: {
        2: false, 3: false, 4: false, 5: false,
        6: false, 7: false, 8: false, 9: false, 10: false,
        11: false, 12: false,
      },
      round: 50,
      error: null,
    };
  },
  computed: {
    tagsString() {
      return Object.keys(this.tags).filter((key) => this.tags[key]).join(',');
    },
    tagList() {
      return this.$store.getters['music/getTagList'];
    },
  },
  methods: {
    async access() {
      console.log(this.tagString)
      this.error = null;
      try {
        const payload = {
          name: this.roomName,
          password: this.password,
          length: this.round,
          mode: 'create',
        }
        if (this.tagsString) {
          payload.tags = this.tagsString
        }
        await this.$store.dispatch('room/accessRoom', payload)
      } catch(error) {
        this.error = error.message || 'Something went wrong!'
      }
      if (this.error === null) {
        this.$router.push(`/room/${this.roomName}`);
      } else {
        console.log(this.error);
      }
    },
    toggleTag(event) {
      this.tags[event.target.value] = !this.tags[event.target.value];
    },
    closeError() {
      this.error = null;
    }
  },
};
</script>

<style scoped>
form {
  margin: 1rem;
  padding: 1rem;
}

.form-control {
  margin: 0.5rem 0;
}

input,
textarea {
  display: block;
  width: 100%;
  font: inherit;
  padding: 0.15rem;
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
  height: inherit;
  width: inherit;
  border-radius: 10px;
}
.active {
  border: white 1px solid;
}

</style>