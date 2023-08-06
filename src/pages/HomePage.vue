<template>
  <div>
    <section>
      <h2>Music List</h2>
      <p>음악 리스트를 확인해 보세요.</p>
    </section>
    <section>
      <h2>Register Music</h2>
      <p>좋아하는 음악을 등록해 보세요.</p>
    </section>
    <section @click="playGame">
      <h2>Play</h2>
      <p>노래 맞추기</p>
    </section>
  </div>
</template>



<script>
export default {
  methods: {
    playGame() {
      this.$router.push('/room/access');
    }
  }
}
</script>

<style scoped>
section {
  width: 100%;
  height: 10rem;
  background-color: rgba(128, 128, 128, 0.2);
  text-align: center;
  vertical-align: center;
  padding: 2rem;
  margin-top: 0.5rem;
}

section:hover {
  background-color: rgba(128, 128, 128, 0.5);
}
</style>