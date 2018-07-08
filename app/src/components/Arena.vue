<template lang="html">
  <div>
    <span>
      <h2>Arena #{{this.$root.user.arena.id}}</h2>
      <h3>active: {{$root.user.arena.start}}, votes remaining: {{$root.user.arena.votes}}</h3>
    </span>
    <div v-for="p in players">
      <div class='box display-board' :style="{ 'background-image': 'url(' + p.image + ')' }">
        <avatar :username="p.username" :src="p.avatar"></avatar>
        <h2>{{p.username}} // {{p.votes}}</h2>
        <button type="button" v-on:click="vote($event, p)" :disabled="p.voted">Vote</button>
        <br>
      </div>
    </div>
    <section class="section">
      <div class="box">
        <div class="drawing-board" id='simple-board'></div>
        <button class="button is-block is-fullwidth" type="button" v-on:click="update_entry()">Submit</button>
      </div>
    </section>
  </div>
</template>

<script>
import DrawingBoard from 'drawingboard/drawingboard.js';
import Avatar from 'vue-avatar';

export default {
  name: 'Arena',
  data() {
    return {
      players: [],
      board: new DrawingBoard.Board('simple-board', {
        background: this.$root.user.entry,
        controls: [{ Navigation: { back: false, forward: false } }],
        webStorage: false,
        enlargeYourContainer: true
      }),
    }
  },
  methods: {
    update_entry() {
      // WARNING: not impl
      this.$http.post('api/u/' + this.$root.user.username, this.board.getImg()).then(response => {
        console.log("Saving..." + response.body);
      }, error => {
        console.log("Error" + response.body);
      });
    },
    vote(e, player) {
      if (this.$root.user.arena.votes <= 0) return;
      this.$root.user.arena.votes -= 1;
      player.votes += 1;
      this._update_votes(player);
      e.target.disabled = true;
    },
    _update_votes(player) {
      this.$http.put('api/arena/' + this.id, [player.username, ]).then(response => {
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    }
  },
  mounted() {
    this.id = this.$route.params.id;

    this.$http.get('api/arena/' + this.id).then(response => {
      if (response.ok) {
        this.players = response.body;
      }
    }, error => {
      console.log(error.status + "  " + error.body);
    });

    //this.board.ev.bind('board:stopDrawing', this.update_entry);
  },
  components: {
    Avatar
  }
}
</script>

<style lang="css">
#simple-board {
  width: 200px;
  height: 200px;
}
.display-board {
  width: 200px;
  height: 200px;
}
</style>
