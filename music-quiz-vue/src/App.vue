<template>
  <div>
    <the-header></the-header>
    <router-view v-slot="slotProps">
      <transition name="route" mode="out-in">
        <component :is="slotProps.Component"></component>
      </transition>
    </router-view>
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
  height: 100%;
  background-color: black;
}

body {
  /* background-image: url('https://cdn.mos.cms.futurecdn.net/HuGGeENt6kGyixe3hT9tnY.jpg'); */
  margin: 0;
  color: white;
}

input {
  /* border: solid 1px rgba(255,255,255,0.5); */
  border: none;
  background-color: rgba(255,255,255,0.1);
  color: white;
  outline: none;
}

label {
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: block;
}
.route-enter-from {
  opacity: 0;
  transform: translateY(-30px);
}

.route-enter-active {
  transition: all 0.3s ease-out;
}

.route-enter-to,
.route-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.route-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.route-leave-active {
  transition: all 0.1s ease-in;
}
</style>