<template lang="html">
  <div>
    <section class="hero is-fullheight is-info">

      <section class="hero-header">
        <nav class="level is-mobile box is-radiusless is-paddingless">
          <div class="level-left">
            <div class="level-item">
              <button class="avatar" @click="enterProfile()">
                <avatar :username="$root.user.username" :src="$root.user.avatar" :rounded='false'></avatar>
              </button>
            </div>
            <div class="level-item has-text-grey ">
              <span class='has-text-weight-light'> u/ </span>
              <span class="is-uppercase"> {{ $root.user.username }} </span>
            </div>
          </div>
          <div class="level-item is-hidden-mobile">
            <span class="is-size-4">Painter Arena</span>
          </div>
          <div class="level-right">
            <div class="level-item">
              <b-dropdown>
                <button class="button is-white is-rounded" slot='trigger'>
                  <b-icon onloadedmetadata=""
                    icon='bell'
                    custom-size='fa-lg'>
                  </b-icon>
                  <b-tag rounded
                  type='is-danger'
                  v-if='this.$root.user.notifications.length'>
                    {this.$root.user.notifications.length}}
                  </b-tag>
                </button>
                <b-dropdown-item custom v-if='this.$root.user.notifications.length == 0' class="has-text-grey-light has-text-centered	">
                  Nothing here!
                </b-dropdown-item>
                <b-dropdown-item v-for='item in this.$root.user.notifications'>
                  {{item.messsage}}
                </b-dropdown-item>
              </b-dropdown>
            </div>
            <div class="level-item">
              <button class="button is-success" type="button" @click.prevent="enterArena">Enter Arena</button>
            </div>
          </div>
        </nav>
      </section>

      <section class="hero-body" style="align-items: normal;">
        <!-- <keep-alive> -->
          <router-view/>
        <!-- </keep-alive> -->
      </section>

      <section class="hero-foot">
      </section>

    </section>
  </div>
</template>

<script>
import Avatar from 'components/Avatar';

export default {
  name: "Main-Page",
  methods: {
    enterProfile() {
      this.$router.push({
        name: "Profile"
      });
    },
    enterArena() {
      if (this.$root.user.arena.id)
        this.$router.push({
          name: "Arena",
          params: {'id': this.$root.user.arena.id}
        });
      this.$http.get('api/match').then(response => { //, {params: {headers: {'Authorization':"Basic dXNlcm5hbWU6cGFzc3dvcmQ="}}}
          console.log(response.body);
          this.$root.user.arena = {...this.$root.user.arena, ...response.body};
          this.$router.push({
            name: "Arena",
            params: {'id': response.body.id}
          });
        }, error => {
          console.log(error.status + "  " + error.body);
        });
    }
  },
  created() {
    if (!this.$root.user.authorized)
      this.$router.push({
        name: "Login"
      });
  },
  components: {
    Avatar
  }

}
</script>

<style scoped lang="css">
  .button .icon:first-child {
    margin-left: calc(-0.375em - 1px);
    margin-right: calc(-0.375em - 1px);
  }
  .tag {
    position: absolute;
    top: calc(100% - ( 1em / 2 ));
    left: calc(100% - ( 1em / 2 ));
    font-size: .5625rem;
    line-height: .375rem;
  }
  .button.is-white {
    color: inherit;
  }
  .header {
    width: 100vw;
  }
  .avatar {
    padding: 0;
    cursor: pointer;
    border:none;
    margin-right: 0.5em;
  }
</style>
