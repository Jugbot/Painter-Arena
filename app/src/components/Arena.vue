<template lang="html">
  <div>
    <div v-for="p in players">
      <div :style="{ 'background-image': 'url(' + p.image + ')' }">
        <h2>p.username</h2>
        <br>
      </div>
    </div>
    <div class="drawing-board" id='simple-board'></div>
  </div>
</template>

<script>
import Vue from 'vue';
import DrawingBoard from '../dist/drawingboard/drawingboard.js';
import io from 'socket.io-client';

export default {
  data() {
    return {
      id: 0,
      players: []
    }
  },
  created() {
      this.id = this.$route.params.id;

      this.$http.get('api/arena/' + this.id).then(response => {
        console.log(response.body);
        if (response.ok) {
          this.players = response.body.players
        }
      }, response => {
        console.log(response.status + "  " + response.body);
      });
  },
  methods: {

  },
  mounted() {

    var simpleBoard = new DrawingBoard.Board('simple-board', {
      //background: this.imageURL(),
      controls: [{ Navigation: { back: false, forward: false } }],
      webStorage: false,
      enlargeYourContainer: true
    });

    for (var p in players) {
      if (p.username == user.username) {
        simpleBoard.setImg(p.entry);
        break;
      }
    }
  }
}
</script>

<style lang="css">
#simple-board {
  width: 200px;
  height: 200px;
}
</style>
