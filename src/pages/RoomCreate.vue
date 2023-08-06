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
        <label for="tags">Tags</label>
        <input id="tags" type="text" v-model.trim="tags"/>
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
      tags: '',
      round: 50,
      error: null,
    }
  },
  methods: {
    async access() {
      this.error = null;
      try {
        await this.$store.dispatch('room/accessRoom',{
        name: this.roomName,
        password: this.password,
        length: this.round,
        tags: this.tags,
        mode: 'create',
      })
      } catch(error) {
        this.error = error.message || 'Something went wrong!'
      }
      if (this.error === null) {
        this.$router.push(`/room/${this.roomName}`);
      } else {
        console.log(this.error);
      }
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

</style>