function make_basic_auth(user, pass) {
  var tok = user + ':' + pass;
  return "Basic " + btoa(tok);
}


var arena_component = Vue.component('arena', {
  template: `
    <div>
      <div v-for="p in players">
        <div :style="{ 'background-image': 'url(' + Vue.http.options.root + 'api/u/' + p.username + '/avatar.png' + ')' width='5em' height='5em'}">
          <h2>p.username</h2>
          <br>
        </div>
      </div>
      <div id='simple-board'></div>
    </div>`,
  data() {
    return {
      players: []
    }
  },
  methods: {

  },
  mounted() {
    var socket = io.connect(Vue.http.options.root);
    socket.on('match_search_progress', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    var simpleBoard = new DrawingBoard.Board('simple-board', {
      //background: this.imageURL(),
      controls: false,
      webStorage: false
    });
  }
});


var main_component = Vue.component('main', {
  template: `
    <div>
      <h2>
        <img class='avatar' :src="imageURL()" alt="not working">
        Welcome [[ user.username ]]
      </h2>
      <button type="button" v-on:click="enterArena">Enter Arena</button>
    </div>`,
  methods: {
    imageURL() {
      return Vue.http.options.root + 'api/u/' + this.user.username + '/avatar.png';
    },
    enterArena() {
      // TODO: flask socketio
      this.router.push({
        name: "arena"
      });
    }
  }
});


var login_component = Vue.component('login', {
  template: `
    <form>
      <input type="text" v-model='user.username' name="username"/><br>
      <input type="password" v-model='user.password' name="password"/><br>
      <button type="button" v-on:click="login">Login</button>
      <button type="button" v-on:click="register">Register</button>
      <h3>[[ message ]]</h3>
    </form>`,
  data() {
    return {
      message: 'Hello Vue!'
    }
  },
  methods: {
    register() {
      this.message = 'waiting...';
      var auth = make_basic_auth(this.user.username, this.user.password);
      Vue.http.headers.common['Authorization'] = auth;
      this.$http.post('api/u/' + this.user.username).then(response => {
        this.message = response.body;
        if (response.ok) {
          setTimeout(() => {
            this.$router.push({
              name: 'user',
              params: {
                id: this.user.username
              }
            }).bind(this);
          }, 1000);
        }
      }, response => {
        this.message = response.status + "  " + response.body;
      });
    },
    login() {
      this.message = 'waiting...';
      var auth = make_basic_auth(this.user.username, this.user.password);
      Vue.http.headers.common['Authorization'] = auth;
      this.$http.get('api/u/' + this.user.username).then(response => {
        this.message = response.body;
        console.log(response.body);
        if (response.ok) {
          setTimeout(() => {
            this.$router.push({
              name: 'user',
              params: {
                id: this.user.username
              }
            }).bind(this);
          }, 1000);
        }
      }, response => {
        this.message = response.status + "  " + response.body;
      });
    }
  }
});


const router = new VueRouter({
  routes: [{
      path: '/',
      redirect: () => {
        return { //TODO: store credentials somehow?
          name: 'login'
        };
      }
    },
    {
      path: '/u/:id',
      name: 'user',
      component: main_component
    },
    {
      path: '/login',
      name: 'login',
      component: login_component
    }

  ]
})


Vue.mixin({ //globals
  delimiters: ["[[", "]]"],
  data: function() {
    return {
      user: {
        username: 'username',
        password: 'password'
      }
    }
  }
});


window.onload = function() {
  Vue.http.options.root = "http://127.0.0.1:5000/";
  var app = new Vue({
    router: router,
    el: '#app'
  });
}
