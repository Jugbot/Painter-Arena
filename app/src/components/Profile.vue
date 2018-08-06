<template lang="html">
  <div class="container is-fluid">

    <div class="corner-button">
      <button class="button is-danger is-small"
        @click="logout()">
        <b-icon icon='door-closed' size='is-small'>
        </b-icon>
        <p>Logout</p>
      </button>
    </div>

    <section class="section">
      <div class="level">
        <div class="level-left">
          <div class="level-item">

            <div id='avatar-wrapper'
            v-show='!editing_avatar'>
              <avatar :username="$root.user.username"
              :src="$root.user.avatar"
              :size="256"
              @click.native.stop='editing_avatar=true'
              :rounded='false'>
              </avatar>
              <div id='edit-icon-wrapper'>
                <b-icon icon='edit'
                type='is-white'></b-icon>
              </div>
            </div>
            <div style="position:relative;" v-show='editing_avatar'>
              <div class="drawing-board" id='simple-board' >
                <button id='bottom-button' class="button is-block is-fullwidth" type="button"
                @click="put_avatar();editing_avatar=false">Submit</button>
              </div>
            </div>

          </div>
        </div>
        <div class="level-item">
          <div>
            <h1 class="is-size-1 has-text-weight-bold has-text-centered">Rating: {{$root.user.skill}}</h1>
            <div class="level">
              <div class="level-item"
                v-if="this.$root.user.arena.id">
                <button class="button is-primary is-large"
                  :class="{'is-loading':match_pending}"
                  @click="post_match()">
                  <b-icon icon='gamepad'>
                  </b-icon>
                  <p>Enter Arena #{{this.$root.user.arena.id}}</p>
                  </button>
              </div>
              <div class="level-item"
                v-if="!this.$root.user.arena.id">
                <button class="button is-success is-large"
                  :class="{'is-loading':match_pending}"
                  @click="post_match()">
                  <b-icon icon='gamepad'>
                  </b-icon>
                  <p>Quickstart</p>
                </button>
              </div>
              <div class="level-item"
                v-if="!this.$root.user.arena.id">
                <button class="button is-primary is-large"
                  :class="{'is-loading':this.match_pending}"
                  @click="arenaModalActive = true">
                  <b-icon icon='cog'>
                  </b-icon>
                  <p>Custom</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <b-modal :active.sync="arenaModalActive" has-modal-card>
      <arena-controls-modal @submit='post_match'></arena-controls-modal>
    </b-modal>

  </div>
</template>

<script>
import Avatar from 'components/Avatar';
import ArenaControlsModal from 'components/ArenaControlsModal';

export default {
  name: "User-Profile",
  components: {
    Avatar,
    ArenaControlsModal
  },
  data() {
    return {
      editing_avatar: false,
      board: null,
      match_pending: false,
      arenaModalActive: false
    }
  },
  methods: {
    put_avatar() {
      let data = new FormData();
      var uri = this.board.getImg();
      data.append('avatar', uri);
      this.$http.put('api/u/' + this.$root.user.username, data).then(response => {
        console.log("Saved");
        this.$root.user.avatar = uri;
      }, error => {
        console.log("Error" + error.body);
      });
    },
    logout() {
      this.$root.reset_all();
    },
    post_match(data={}) {
      console.log(data);
      this.match_pending = true;
      if (this.$root.user.arena.id)
        this.$router.push({
          name: "Arena",
          params: {'id': this.$root.user.arena.id}
        });
      this.$http.post('api/match', data).then(response => { //, {params: {headers: {'Authorization':"Basic dXNlcm5hbWU6cGFzc3dvcmQ="}}}
          console.log(response.body);
          this.$root.user.arena = {...this.$root.user.arena, ...response.body};
          this.$router.push({
            name: "Arena",
            params: {'id': response.body.id}
          });
        }, error => {
          console.log(error.status + "  " + error.body);
          this.match_pending = false;
        });
    }
  },
  created() {
    this.$http.get('api/u/' + this.$root.user.username).then(response => {
      this.$root.user = {...this.$root.user, ...response.body};
    });
  },
  mounted() {
    this.board = new DrawingBoard.Board('simple-board', {
      // background: this.$root.user.entry,
      controls: [{ Navigation: { back: false, forward: false } }],
      webStorage: false,
      enlargeYourContainer: true,
      controlsPosition: 'bottom right'
    });

    this.board.setImg(this.$root.user.avatar);
  }
}
</script>

<style lang="css">
.slight-white {
   color: rgba(255,255,255,0.2);
}
.big-button {
  width: 10em !important;
  height: 10em !important;
}
#edit-icon-wrapper {
  position:absolute;
  right:5px;
  top:5px;
  text-shadow: 0px 0px 1px #000;
  display:none;
}
#avatar-wrapper:hover #edit-icon-wrapper {
  display:block;
}
#avatar-wrapper {
  position: relative;
  cursor: pointer;
}
#bottom-button, .drawing-board-controls {
  position: absolute;
  top:100%;
}
</style>

<!-- <button class="button is-primary is-large big-button"
  @click="arenaModalActive = true">
  <span class="icon slight-white">
    <i class="fas fa-cog fa-8x"></i>
    <p class="is-size-2 has-text-white" style="position: absolute;top:100%;">Custom</p>
  </span>
</button> -->
