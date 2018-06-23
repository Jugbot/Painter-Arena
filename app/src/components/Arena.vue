<template lang="html">
  <div>
    <div v-for="p in players">
      <div :style="{ 'background-image': 'url(' + Vue.http.options.root + 'api/u/' + p.username + '/avatar.png' + ')' }">
        <h2>p.username</h2>
        <br>
      </div>
    </div>
    <div id='simple-board'></div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      players: []
    }
  },
  methods: {

  },
  mounted() {
    var socket = io.connect(Vue.http.options.root);
    socket.on('match_search_progress', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    var simpleBoard = new DrawingBoard.Board('simple-board', {
      //background: this.imageURL(),
      controls: false,
      webStorage: false
    });
  }
}
</script>

<style lang="css">
</style>
