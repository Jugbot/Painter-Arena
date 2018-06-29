<template lang="html">
  <div>
    <input type="text" v-model='$root.user.username' name="username"/><br>
    <input type="password" v-model='$root.user.password' name="password"/><br>
    <button type="button" v-on:click="login">Login</button>
    <button type="button" v-on:click="register">Register</button>
    <h3>{{ message }}</h3>
  </div>
</template>

<script>
import Vue from 'vue';

export default {
  name: 'Login-Page',
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  methods: {
    _make_basic_auth(user, pass) {
      var tok = user + ':' + pass;
      return "Basic " + btoa(tok);
    },
    _fetch_user(protocol) {
      this.message = 'waiting...';
      var auth = this._make_basic_auth(this.$root.user.username, this.$root.user.password);
      Vue.http.headers.common['Authorization'] = auth;
      this.$http[protocol]('api/u/' + this.$root.user.username).then(response => {
        this.message = "Success";
        if (response.body.authorized) {
          this.$root.user = {...this.$root.user, ...response.body};
          console.log(this);
          setTimeout(() => {
            this.$router.push({
              name: 'Profile',
              params: {
                id: this.$root.user.username
              }
            });
          }, 1000);
        }
      }, response => {
        this.message = response.body;
        console.log(response.status + "  " + response.body);
      });
    },
    register() {
      this._fetch_user('post');
    },
    login() {
      this._fetch_user('get');
    }
  }
}
</script>

<style lang="css">
</style>
