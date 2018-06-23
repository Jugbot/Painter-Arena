<template lang="html">
  <div>
    <h2>
      <img class='avatar' :src="imageURL()" alt="not working" width='5em'>
      Welcome {{ user.username }}
    </h2>
    <button type="button" v-on:click="enterArena">Enter Arena</button>
  </div>
</template>

<script>
export default {
  methods: {
    imageURL() {
      return Vue.http.options.root + 'api/u/' + this.user.username + '/avatar.png';
    },
    enterArena() {
      // TODO: flask socketio
      this.router.push({
        name: "arena"
      });
    }
  }

}
</script>

<style lang="css">
</style>
