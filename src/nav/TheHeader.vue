<template>
  <header>
    <nav>
      <h1>
        <base-button link to="/home" mode="flat">Music Quiz</base-button>
      </h1>
      <ul>
        <li>
          <base-button @click="changeMode">{{ buttonName }}</base-button>
        </li>
        <li>
          <base-button @click="autoLogin" v-if="!isLoggedin">Login</base-button>
          <base-button @click="logout" v-else>Logout</base-button>
        </li>
      </ul>
    </nav>
  </header>
</template>

<script>
export default {
  computed: {
    isLoggedin() {
      return this.$store.getters['isAuthenticated'];
    },
    buttonName() {
      if (this.$route.path === '/room/access') {
        return 'Create Room';
      } else if (this.$route.path === '/room/create') {
        return 'Access Room';
      } else {
        return 'Play'
      }
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('logout');
      this.$router.replace('/home');
    },
    autoLogin() {
      this.$store.dispatch('autoLogin');
      if (this.isLoggedin) {
        this.$router.push('/home');
      } else {
        this.$router.push('/auth')
      }
    },
    changeMode() {
      if (this.$route.path === '/room/access') {
        this.$router.push('/room/create');
      } else {
        this.$router.push('/room/access');
      }
    }
  }
};
</script>

<style scoped>
header {
  width: 100%;
  height: 5rem;
  background-color: black;
  display: flex;
  justify-content: center;
  align-items: center;
}

header a {
  text-decoration: none;
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border: 1px solid transparent;
}

h1 {
  margin: 0;
}

header nav {
  width: 90%;
  margin: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

li {
  margin: 0 0.5rem;
}
</style>