<template lang="html">
  <div>
    <input type="text" v-model='user.username' name="username"/><br>
    <input type="password" v-model='user.password' name="password"/><br>
    <button type="button" v-on:click="login">Login</button>
    <button type="button" v-on:click="register">Register</button>
    <h3>{{ message }}</h3>
  </div>
</template>

<script>
import Vue from 'vue';

export default {
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  methods: {
    make_basic_auth(user, pass) {
      var tok = user + ':' + pass;
      return "Basic " + btoa(tok);
    },
    register() {
      this.message = 'waiting...';
      var auth = this.make_basic_auth(this.user.username, this.user.password);
      Vue.http.headers.common['Authorization'] = auth;
      this.$http.post('api/u/' + this.user.username).then(response => {
        this.message = response.body;
        if (response.ok) {
          setTimeout(() => {
            this.$router.push({
              name: 'Main',
              params: {
                id: this.user.username
              }
            });
          }, 1000);
        }
      }, response => {
        this.message = response.status + "  " + response.body;
      });
    },
    login() {
      this.message = 'waiting...';
      var auth = this.make_basic_auth(this.user.username, this.user.password);
      Vue.http.headers.common['Authorization'] = auth;
      this.$http.get('api/u/' + this.user.username).then(response => {
        this.message = response.body;
        console.log(response.body);
        if (response.ok) {
          setTimeout(() => {
            this.$router.push({
              name: 'Main',
              params: {
                id: this.user.username
              }
            });
          }, 1000);
        }
      }, response => {
        this.message = response.status + "  " + response.body;
      });
    }
  }
}
</script>

<style lang="css">
</style>
