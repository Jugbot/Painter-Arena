<template lang="html">
  <div class="container is-fluid">

    <div class="corner-button">
      <button class="button is-danger is-small"
        @click="delete_match()">
        <b-icon icon='door-closed' size='is-small'>
        </b-icon>
        <p>Exit</p>
      </button>
    </div>

    <section class="hero">
      <div class="hero-head">
        <div class="container has-text-centered">
          <h1 class="title is-1">Arena #{{$root.user.arena.id}}</h1>
          <h2 class="subtitle is-6 has-text-grey-lighter" v-if='$root.user.arena.start'>
            <countdown :date='$root.user.arena.timeout' @timeout="end()"></countdown>
          </h2>
        </div>
      </div>
      <div class="hero-body">
        <div class="container has-text-centered" v-if='$root.user.arena.prompt'>
          <b-icon icon='quote-left' size='is-small' style="vertical-align: super;"></b-icon>
          <span class='is-size-3' style='padding: 0 0.5em;'>{{$root.user.arena.prompt}}</span>
          <b-icon icon='quote-right' size='is-small' style="vertical-align: sub;"></b-icon>
        </div>
      </div>
      <div class="hero-foot">
        <div class="steps">
          <div class="step-item" :class="{ 'is-active': (step >= 0)}">
            <div class="step-marker">1</div>
            <div class="step-details">
              <p class="step-title">Matching</p>
              <p v-if="this.step == 0"><span class="has-text-grey-lighter">{{Object.keys(players).length}}</span> / {{$root.user.arena.max_players}}</p>
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
            :data="list_players"
            :default-sort='["votes","desc"]'
            :mobile-cards='false'>
              <template slot-scope="props">
                <b-table-column field="username" label="User">
                  {{ props.row.username }}
                </b-table-column>
                <b-table-column field="votes" label="Votes"
                :visible='$root.user.arena.start'
                numeric>
                  <span class="tag is-success" :class='{"is-visible": props.row.entry}'>
                    {{ props.row.votes }}
                  </span>
                </b-table-column>
              </template>
            </b-table>
        </b-tab-item>

        <b-tab-item label="Gallery" icon='th-large' :disabled='!$root.user.arena.start'>
            <div class='container'>
              <!-- <h1 class="title" v-if='players.length == 0'>Nothing submitted yet :/</h1> -->
              <div class="grid">
                <div class='grid_item box display-board animated fadeIn'
                :style="{ 'background-image':'url(' + p.entry + ')' }"
                @click.self="expand(p.entry)"
                v-for="(p, username) in players"
                v-if='p.entry'>
                  <b-field class="upvote-header" v-if='username != $root.user.username'>
                    <b-checkbox-button
                      v-model="$root.user.arena.voted_users"
                      :native-value='username'
                      @input.native="vote(p, username, $event)"
                      type="is-success">
                      <i class="fas fa-check fa-sm"></i>
                    </b-checkbox-button>
                  </b-field>
                  <footer class="media media-footer is-unselectable">
                    <figure class="media-left">
                      <avatar :username="username" :src="p.avatar"></avatar>
                    </figure>
                    <div class="media-content">
                      <div class="content">
                        <p>
                          <strong>{{username}}</strong>
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
                <button class="button is-block is-fullwidth" type="button" @click="put_entry()">Submit</button>
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
import merge from 'deepmerge'

export default {
  name: 'Arena',
  data() {
    return {
      players: {},
      board: null,
      id: -1
    }
  },
  computed: {
    list_players() {
      return Object.keys(this.players).map(key =>
        ({'username': key, ...this.players[key]})
      );
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
      this.$router.push({
        name: "Profile",
        params: {'id': this.$root.user.username}
      });
      this.$root.reset_arena();
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
    put_entry() {
      let data = new FormData();
      var uri = this.board.getImg();
      data.append('entry', uri);
      this.$http.put('api/u/' + this.$root.user.username, data).then(response => {
        console.log("Saved");
        this.$root.user.entry = uri;
        this.get_players();
      }, error => {
        console.log("Error" + error.body);
      });
    },
    delete_match() {
      this.$http.delete('api/match').then(response => {
          console.log(response.body);
          this.end();
        }, error => {
          console.log(error.status + "  " + error.body);
        });
    },
    vote(player, username, state) {
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
      this.put_votes(player, username);
    },
    put_votes(player, username) {
      this.$http.put('api/arena/' + this.id, [username, ]).then(response => {
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    },
    get_players() {
      console.log('updating players');
      this.$http.get('api/arena/' + this.id).then(response => {
        this.players = response.body;
      }, error => {
        console.log(error.status + "  " + error.body);
      });
      this.get_arena();
    },
    get_arena() {
      this.$http.get('api/u/' + this.$root.user.username, {'params': {'items': ['arena',]}}).then(response => {
        this.$root.user.arena = {...this.$root.user.arena, ...response.body.arena};
      });
    },
    //SOCKETS
    player_join(data) {
      console.log('join', data);
      this.players = {...this.players, ...data}
      if (!this.$root.user.arena.start && Object.keys(this.players).length >= this.$root.user.arena.max_players)
        this.get_arena();
    },
    player_leave(data) {
      console.log('leave', data);
      this.$delete(this.players, data['username'])
    },
    entry_update(data) {
      console.log('entry', data);
      this.players = merge(this.players, data)
    },
    votes_changed(data) {
      console.log('votes', data);
      this.players = merge(this.players, data)
    }
  },
  created() {
    // if (this.id != this.$route.params.id)
    //   this.players = [];
    this.id = this.$route.params.id;
    this.$socket.emit('subscribe', this.id); //join socket room
    this.get_players();

    this.$options.sockets.player_join = this.player_join;
    this.$options.sockets.player_leave = this.player_leave;
    this.$options.sockets.entry_update = this.entry_update;
    this.$options.sockets.votes_changed = this.votes_changed;
    this.$options.sockets.reconnect = this.update_players;
  },
  beforeDestroy() {
    delete this.$options.sockets.player_join;
    delete this.$options.sockets.player_leave;
    delete this.$options.sockets.entry_update;
    delete this.$options.sockets.votes_changed;
    delete this.$options.sockets.reconnect;
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
  width: 256px;
  height: 256px;
}

.corner-button {
  position: absolute;
  right: 0;
  top: 0;
  z-index: 9;
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

/* Responsive Tabs */
@media screen and (max-width: 768px) {
  li:not(.is-active) > a > span:not(.icon) {
    visibility: hidden;
    position:  absolute;
  }

  nav.tabs li:not(.is-active) {
    -webkit-box-flex: 0;
    -ms-flex-positive: 0;
    flex-grow: 0;
    -ms-flex-negative: 1;
    flex-shrink: 1;
  }

  .tabs .icon {
    margin-left: 0.5em;
  }
}

.tabs li {
  transition: flex-grow 1s ease;
}
</style>
