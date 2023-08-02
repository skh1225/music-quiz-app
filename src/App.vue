<template>
  <div>
    <the-header></the-header>
    <router-view></router-view>
  </div>
</template>

<script>
import TheHeader from './nav/TheHeader.vue';

export default {
  components: {
    TheHeader,
  }
}
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap");

* {
  box-sizing: border-box;
}

html {
  font-family: "Roboto", sans-serif;
}

body {
  /* background-image: url('https://cdn.mos.cms.futurecdn.net/HuGGeENt6kGyixe3hT9tnY.jpg'); */
  margin: 0;
  background-color: black;
  color: white;
}
</style>