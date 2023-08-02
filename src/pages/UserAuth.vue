<template>
  <div>
    <base-dialog :show="!!error" @close="closeError">{{ error }}</base-dialog>
    <form @submit.prevent="login">
      <div class="form-control">
        <label for="email">E-Mail</label>
        <input id="email" type="email" v-model.trim="email"/>
      </div>
      <div class="form-control">
        <label for="password">Password</label>
        <input id="password" type="password" v-model.trim="password"/>
      </div>
      <base-button>Login</base-button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      error: null,
    }
  },
  computed: {
    isLoggedin() {
      return this.$store.getters['isAuthenticated'];
    }
  },
  methods: {
    async login() {
      try {
        await this.$store.dispatch('login', {
        email: this.email,
        password: this.password,
      })} catch(error) {
        this.error = error.message || 'Something went wrong!';
      }
      if (this.error === null) {
        this.$router.replace('/home')
      } else {
        console.log(this.error)
      }
    },
    closeError() {
      this.error = null;
    }
  },
  create() {
    this.$store.dispatch('autoLogin');
    if (this.isLoggedin) {
      this.$router.replace('/home');
    }
  }
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