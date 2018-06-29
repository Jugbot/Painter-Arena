<template lang="html">
  <div>
    <div class="header">
      <h2>
        <avatar :username="$root.user.username" :src="$root.user.avatar"></avatar>
        <!-- <img class='avatar' :src="$root.safe_avatar" alt="not working"> -->
        Welcome {{ $root.user.username }}
      </h2>
      <button type="button" v-on:click="enterArena">Enter Arena</button>
    </div>
    <router-view/>
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

<style lang="css">
  .header {
    width: 100vw;
  }
  .avatar {
    width: 2em;
  }
</style>
