<template lang="html">
  <div class="container is-fluid">
    <section class="hero">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title">Arena #{{this.$root.user.arena.id}}</h1>
          <h2 class="subtitle">active: {{$root.user.arena.start}}, votes remaining: {{$root.user.arena.votes}}</h2>
        </div>
      </div>
    </section>

    <section class="section">
      <div class='container'>
        <div class="grid">

          <div class='grid_item box display-board' :style="{ 'background-image':'url(' + p.image + ')' }"  v-for="p in players">
            <div class="overlay-board is-overlay">
              <avatar :username="p.username" :src="p.avatar"></avatar>
              <span>{{p.username}} // {{p.votes}}</span>
              <b-field>
                <b-checkbox-button
                  v-model="$root.user.arena.voted_users"
                  :native-value='p.username'
                  @click.native="vote(p)"
                  type="is-success">
                  <span>vote</span>
                  <!-- @click.native="vote($event, p)" -->
                </b-checkbox-button>
              </b-field>
            </div>
          </div>

        </div>
      </div>
    </section>

    <section class="section">
      <div class='container'>
        <div class="box">
          <div class="drawing-board" id='simple-board'></div>
          <button class="button is-block is-fullwidth" type="button" v-on:click="update_entry()">Submit</button>
        </div>
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
    vote(player) {
      if (this.$root.user.arena.votes <= 0) return;
      this.$root.user.arena.votes -= 1;
      player.votes += 1;
      this._update_votes(player);
      console.log("voted");
    },
    _update_votes(player) {
      this.$http.put('api/arena/' + this.id, [player.username, ]).then(response => {
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    }
  },
  created() {
    this.id = this.$route.params.id;

    this.$http.get('api/arena/' + this.id).then(response => {
      if (response.ok) {
        this.players = response.body;
      }
    }, error => {
      console.log(error.status + "  " + error.body);
    });
  },
  components: {
    Avatar
  }
}
</script>

<style scoped lang="css">
#simple-board {
  width: 200px;
  height: 200px;
}

.overlay-board {
  border-radius: inherit;
  background-color: rgba(0,0,0,0.3);
  opacity: 0;
  transition: 0.2s ease;
}

.display-board {
  width: 200px;
  height: 200px;
  background-repeat: no-repeat;
  background-size: cover;
  background-image: url(http://via.placeholder.com/128x128);
}

.display-board:hover .overlay-board {
  opacity: 1;
}

.grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

.grid .grid_item {
  position: relative;
  margin: 0 15px 30px 15px;
}
</style>
