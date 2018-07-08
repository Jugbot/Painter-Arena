<template lang="html">
  <div>
    <section class="hero is-success is-fullheight">
      <div class="hero-body">
        <div class="container has-text-centered">
          <div class="column is-4 is-offset-4">
            <h3 class="title has-text-grey">Login</h3>
            <p class="subtitle has-text-grey">Please login to proceed.</p>
            <div class="box">
              <figure class="avatar">
                <avatar :username="$root.user.username" :src="$root.user.avatar" size="128"></avatar>
              </figure>
              <form>
                <b-field>
                  <div class="control">
                    <b-input size="is-large"
                    v-model='$root.user.username'
                    placeholder="username"
                    max='16'
                    autofocus></b-input>
                  </div>
                </b-field>

                <b-field>
                  <div class="control">
                    <b-input size="is-large"
                    v-model='$root.user.password'
                    placeholder="password"
                    type="password"
                    v-on:focus="valid_user()"
                    max='128'></b-input>
                  </div>
                </b-field>
                <b-field>
                  <label class="checkbox">
                    <b-checkbox>
                    </b-checkbox>
                    Remember me
                  </label>
                </b-field>
                <button class="button is-block is-info is-large is-fullwidth" v-on:click="fetch_user()">{{this.message}}</button>
              </form>
            </div>
              <p class="has-text-grey">
                <a href="../">Sign Up</a> &nbsp;·&nbsp;
                <a href="../">Forgot Password</a> &nbsp;·&nbsp;
                <a href="../">Need Help?</a>
              </p>
            </div>
          </div>
        </div>
      </section>
  </div>
</template>

<script>
import Vue from 'vue';
import Avatar from 'vue-avatar';

export default {
  name: 'Login-Page',
  data() {
    return {
      method: "get",
      message: 'Login',
      pending: false
    }
  },
  methods: {
    _make_basic_auth() {
      var tok = this.$root.user.username + ':' + this.$root.user.password;
      Vue.http.headers.common['Authorization'] = "Basic " + btoa(tok);
    },
    fetch_user(protocol = this.method) {
      this._make_basic_auth();
      this.$http[protocol]('api/u/' + this.$root.user.username).then(response => {
        if (response.body.authorized) {
          this.$toast.open({
                      message: 'Welcome ' + this.$root.user.username + "!",
                      type: 'is-success'
                  });
          this.$root.user = {...this.$root.user, ...response.body};
          setTimeout(() => {
            this.$router.push({
              name: 'Profile',
              params: {
                id: this.$root.user.username
              }
            });
          }, 1000);
        }
      }, error => {
        console.log(error.status + "  " + error.body);
      });
    },
    register() {
      this.fetch_user('post');
    },
    login() {
      this.fetch_user('get');
    },
    valid_user() {
      this.$http.get('api/u/' + this.$root.user.username).then(response => {
        this.message = "Login";
        this.method = "get";
      }, error => {
        this.message = "Register";
        this.method = 'post';
      });
    }
  },
  components: {
    Avatar
  }
}
</script>

<style scoped lang="css">
.hero.is-success {
  background: #F2F6FA;
}
.box {
  margin-top: 5rem;
}
.avatar {
  margin-top: -70px;
  padding-bottom: 20px;
  width: 100%;
  display: flex;
  justify-content: center;
}
.avatar div {
  border: 5px solid #fff;
  background: #fff;
  border-radius: 50%;
  -webkit-box-shadow: 0 2px 3px rgba(10,10,10,.1), 0 0 0 1px rgba(10,10,10,.1);
  box-shadow: 0 2px 3px rgba(10,10,10,.1), 0 0 0 1px rgba(10,10,10,.1);
}
</style>
