<template lang="html">
  <div class="container is-fluid">
    <section class="hero">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title is-size-1">Arena #{{$root.user.arena.id}}</h1>
          <h2 class="subtitle" v-if='$root.user.arena.start'>
            <countdown :date='$root.user.arena.timeout' @timeout="end()"></countdown>
          </h2>
        </div>
      </div>
      <div class="hero-foot">
        <div class="steps">
          <div class="step-item" :class="{ 'is-active': (step >= 0)}">
            <div class="step-marker">1</div>
            <div class="step-details">
              <p class="step-title">Matching</p>
              <p v-if="this.step == 0"><span class="has-text-grey-lighter">{{this.players.length}}</span> / 10</p>
            </div>
          </div>
          <div class="step-item" :class="{ 'is-active': (step >= 1)}">
            <div class="step-marker">2</div>
            <div class="step-details">
              <p class="step-title">Draw</p>
              <p v-if='this.step == 1'>Draw your entry in the <b-tag rounded>Canvas</b-tag> tab.</p>
            </div>
          </div>
          <div class="step-item" :class="{ 'is-active': (step >= 2)}">
            <div class="step-marker">3</div>
            <div class="step-details">
              <p class="step-title">Submit</p>
              <p v-if='this.step == 2'>Don't forget to vote on other entries as they appear!
                <b-tag rounded>{{$root.user.arena.votes}} votes</b-tag> remaining.
              </p>
            </div>
          </div>
          <div class="step-item" :class="{ 'is-active': (step >= 3)}">
            <div class="step-marker">4</div>
            <div class="step-details">
              <p class="step-title">Vote</p>
              <p v-if='this.step == 3'>Now all you need to do is wait for the results...</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <b-tabs type="is-toggle" expanded>
        <b-tab-item label='Placements' icon="medal">
            <b-table
            :data="sorted_players"
            default-sort-direction="desc">
              <template slot-scope="props">
                <b-table-column field="votes" label="Votes">
                  <span class="tag is-success">
                    {{ props.row.votes }}
                  </span>
                </b-table-column>
                <b-table-column field="username" label="User">
                  {{ props.row.username }}
                </b-table-column>
              </template>
            </b-table>
        </b-tab-item>

        <b-tab-item label="Gallery" icon='th-large'>
            <div class='container'>
              <div class="grid">

                <div class='grid_item box display-board animated fadeIn' :style="{ 'background-image':'url(' + p.image + ')' }" @click.self="expand(p.image)" v-for="p in sorted_players" v-if='p.image'>
                  <b-field class="upvote-header" v-if='p.username != $root.user.username'>
                    <!-- <div class="control"><label tabindex="0" class="b-checkbox checkbox button is-success"><i class="fas fa-check fa-sm"></i> <input type="checkbox" value="user6"></label></div> -->
                    <b-checkbox-button
                      v-model="$root.user.arena.voted_users"
                      :native-value='p.username'
                      @input.native="vote(p, $event)"
                      type="is-success">
                      <i class="fas fa-check fa-sm"></i>
                    </b-checkbox-button>
                  </b-field>
                  <footer class="media media-footer is-unselectable">
                    <figure class="media-left">
                      <avatar :username="p.username" :src="p.avatar"></avatar>
                    </figure>
                    <div class="media-content">
                      <div class="content">
                        <p>
                          <strong>{{p.username}}</strong>
                          <br>
                          <small>votes: {{p.votes}}</small>
                        </p>
                      </div>
                    </div>
                  </footer>

                </div>
              </div>
            </div>
        </b-tab-item>

        <b-tab-item label="Canvas" icon='paint-brush' :disabled='!$root.user.arena.start'>
          <div class='level'>
            <div class="level-item">
              <div class="box">
                <div class="drawing-board" id='simple-board'></div>
                <button class="button is-block is-fullwidth" type="button" @click="update_entry()">Submit</button>
              </div>
            </div>
          </div>
        </b-tab-item>
      </b-tabs>
    </section>

  </div>
</template>

<script>
import DrawingBoard from 'drawingboard/drawingboard.js';
import Avatar from 'components/Avatar';
import ExpandedImageModal from 'components/ExpandedImageModal'
import Countdown from 'components/Countdown'


export default {
  name: 'Arena',
  data() {
    return {
      players: [],
      board: null,
      id: -1
    }
  },
  computed: {
    sorted_players() {
      return this.players.slice().sort((p1,p2) => {
        return p1.votes-p2.votes;
      });
    },
    arena_state() {
      if (this.$root.user.arena.start)
        return ["live", "is-success"];
      return ["pending", "is-warning"];
    },
    step() {
      if (this.$root.user.arena.votes <= 0)
        return 3;
      if (this.$root.user.entry)
        return 2;
      if (this.$root.user.arena.start)
        return 1;
      return 0;
    }
  },
  methods: {
    end() {
      this.$http.get('api/u/' + this.$root.user.username).then(response => {
        this.$root.user = {...this.$root.user, ...response.body};
      });
      this.$router.push({
        name: "Profile"
      });
    },
    expand(image) {
      this.$modal.open({
            parent: this,
            component: ExpandedImageModal,
            props: {
              'image': image
            },
            hasModalCard: true
          });
    },
    update_entry() {
      let data = new FormData();
      var uri = this.board.getImg();
      data.append('entry', uri);
      this.$http.put('api/u/' + this.$root.user.username, data).then(response => {
        console.log("Saved");
        this.$root.user.entry = uri;
        this.update_players();
      }, error => {
        console.log("Error" + error.body);
      });
    },
    vote(player, state) {
      console.log(state);
      if (state.target.checked) {
        if (this.$root.user.arena.votes <= 0) return;
        this.$root.user.arena.votes -= 1;
        player.votes += 1;
        console.log("voted");
      } else {
        this.$root.user.arena.votes += 1;
        player.votes -= 1;
        console.log("unvoted");
      }
      this._update_votes(player);
    },
    _update_votes(player) {
      this.$http.put('api/arena/' + this.id, [player.username, ]).then(response => {
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    },
    update_players() {
      console.log('updating players');
      this.$http.get('api/arena/' + this.id).then(response => {
        if (response.ok) {
          this.players = response.body;
        }
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    },
    //SOCKETS
    player_join(data) {
      console.log('join');
      if (data.username != this.$root.user.username)
        this.update_players(); //inefficient but it will do
    },
    entry_update(data) {
      console.log('entry');
      p = this.players.find(o => o.username == data.username);
      p.entry = data.entry;
    },
    votes_changed(data) {
      console.log('votes');
      p = this.players.find(o => o.username == data.username);
      p.votes = data.votes;
    }
  },
  created() {
    // if (this.id != this.$route.params.id)
    //   this.players = [];
    this.id = this.$route.params.id;
    this.$socket.emit('join', this.$root.user.username, this.id);
    this.update_players();

    this.$options.sockets.player_join = this.player_join;
    this.$options.sockets.entry_update = this.entry_update;
    this.$options.sockets.votes_changed = this.votes_changed;

  },
  onBeforeDestroy() {
    delete this.$options.sockets.player_join;
    delete this.$options.sockets.entry_update;
    delete this.$options.sockets.votes_changed;
  },
  mounted() {
    this.board = new DrawingBoard.Board('simple-board', {
      // background: this.$root.user.entry,
      controls: [{ Navigation: { back: false, forward: false } }],
      webStorage: false,
      enlargeYourContainer: true
    });

    this.board.setImg(this.$root.user.entry);
  },
  // persist: ['players', 'id'],
  components: {
    Avatar,
    Countdown
  }
}
</script>

<style lang="css">
#simple-board {
  width: 200px;
  height: 200px;
}

.b-checkbox.checkbox.button {
    border-radius: 0px;
    border-top-right-radius: 4px !important;
    border-bottom-left-radius: 100% !important;
}

.upvote-header {
  position: absolute;
  top: 0;
  right: 0;
}

.display-board {
  width: 200px;
  height: 200px;
  background-repeat: no-repeat;
  background-size: cover;
  background-image: url(http://via.placeholder.com/128x128);
}

.display-board:hover .media-footer {
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

.media-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  border-radius: inherit;
  opacity: 0;
  transition: 0.2s ease;
  padding: 1rem 1.5rem 1rem;
  background: linear-gradient(rgba(36,38,38,0) 0,rgba(36,38,38,.75) 100%);
}
</style>
