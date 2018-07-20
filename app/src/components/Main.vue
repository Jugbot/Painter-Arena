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
              <button class="button is-success" type="button" @click.prevent="enterArena">Enter Arena</button>
            </div>
          </div>
        </nav>
      </section>

      <section class="hero-body" style="align-items: normal;">
        <keep-alive>
          <router-view/>
        </keep-alive>
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
