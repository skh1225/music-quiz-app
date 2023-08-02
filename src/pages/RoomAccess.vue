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
      <base-button>Access</base-button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      roomName: '',
      password: '',
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
        mode: 'access',
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

label {
  font-weight: bold;
  color: white;
  margin-bottom: 0.5rem;
  display: block;
}

input,
textarea {
  display: block;
  width: 100%;
  font: inherit;
  border: 1px solid #ccc;
  padding: 0.15rem;
}

input:focus,
textarea:focus {
  border-color: #3d008d;
  background-color: #faf6ff;
  outline: none;
}

.errors {
  font-weight: bold;
  color: red;
}

.actions {
  text-align: center;
}
</style>