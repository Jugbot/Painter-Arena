<template lang="html">
  <div>
    <section class="hero is-fullheight is-info">

      <section class="hero-header">
        <nav class="level is-mobile">
          <div class="level-left">
            <div class="level-item">
              <figure class="avatar">
                <avatar :username="$root.user.username" :src="$root.user.avatar"></avatar>
              </figure>
              <h2>{{ $root.user.username }}</h2>
            </div>
          </div>
          <div class="level-item">
            <h1>Painter Arena</h1>
          </div>
          <div class="level-right">
            <div class="level-item">
              <button class="button is-success" type="button" v-on:click="enterArena">Enter Arena</button>
            </div>
          </div>
        </nav>
      </section>

      <section class="hero-body">
        <router-view/>
      </section>

      <section class="hero-footer">
      </section>

    </section>
  </div>
</template>

<script>
import Avatar from 'vue-avatar';

export default {
  name: "Main-Page",
  methods: {
    enterArena() {
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
    console.log(this);
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
    margin: 0.5em;
  }
</style>
