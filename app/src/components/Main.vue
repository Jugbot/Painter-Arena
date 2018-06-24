<template lang="html">
  <div>
    <h2>
      <img class='avatar' :src="imageURL()" alt="not working">
      Welcome {{ user.username }}
    </h2>
    <button type="button" v-on:click="enterArena">Enter Arena</button>
  </div>
</template>

<script>
import io from 'socket.io-client';

export default {
  methods: {
    imageURL() {
      return this.http.root + 'api/u/' + this.user.username + '/avatar.png';
    },
    enterArena() {
      // TODO: flask socketio
      this.$http.get('api/match').then(response => {
          console.log(response.body);
        }, response => {
          console.log(response.status + "  " + response.body);
        });
    }
  },
  mounted() {
      var socket = io.connect(this.http.root);
      socket.on('match_search_progress', function(content, rinfo) {
        console.log(content);

        // this.$router.push({
        //   name: "Arena",
        //   params: {}
        // });
      });
  }

}
</script>

<style lang="css">
  .avatar {
    width: 2em;
  }
</style>
