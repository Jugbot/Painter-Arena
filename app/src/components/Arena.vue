<template lang="html">
  <div class="container is-fluid">
    <section class="hero">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title is-size-1">Arena #{{$root.user.arena.id}}</h1>
          <h2 class="subtitle" v-if='$root.user.arena.start'>
            <countdown :date='$root.user.arena.timeout' :timeout="end()"></countdown>
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
    // FIXME: fires three times
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
      this.$http.get('api/arena/' + this.id).then(response => {
        if (response.ok) {
          this.players = response.body;
        }
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    }
  },
  created() {
    this.id = this.$route.params.id;

    this.update_players();
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

/* .white-border {
  border-color: #dbdbdb;
  border-style: solid;
  border-width: 1px;
}

span.is-pulled-right {
  margin-left: 1rem;
} */

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


<!-- <div class="level">
  <div class="level-left">
    <div class="level-item">
      <h1 class="title is-size-1">Arena #{{$root.user.arena.id}}</h1>
    </div>
  </div>
  <div class="level-right">
    <div class="level-item">
      <div class="has-text-right">
        <p>
          state
          <span class="is-pulled-right">{{this.arena_state[0]}}</span>
        </p>
        <p>
          votes
          <span class="is-pulled-right">{{$root.user.arena.votes}}</span>
        </p>
        <p class="has-text-centered" v-if='$root.user.arena.active'>
          timeout <br>
          <Countdown :date='$root.user.arena.timeout'></Countdown>
        </p>
      </div>
    </div>
  </div>
</div> -->
<!-- <b-field grouped group-multiline style='display: flex; justify-content: center;'>
  <div class="control">
    <b-taglist attached>
      <b-tag size="is-medium">state</b-tag>
      <b-tag size="is-medium" :type="arena_state[1]">{{this.arena_state[0]}}</b-tag>
    </b-taglist>
  </div>
  <div class="control">
    <b-taglist attached>
      <b-tag size="is-medium">remaining votes</b-tag>
      <b-tag size="is-medium" type="is-primary">{{$root.user.arena.votes}}</b-tag>
    </b-taglist>
  </div>
  <div class="control" v-if='$root.user.arena.active'>
    <b-taglist attached>
      <b-tag size="is-medium">time remaining</b-tag>
      <b-tag size="is-medium" type="is-dark">
        <Countdown :date='$root.user.arena.timeout'></Countdown>
      </b-tag>
    </b-taglist>
  </div>
</b-field> -->
