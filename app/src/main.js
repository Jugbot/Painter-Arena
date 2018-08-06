import Vue from 'vue'
import Resource from 'vue-resource'
import App from 'App'
import router from 'router/index'
import Buefy from 'buefy'
import 'buefy/lib/buefy.css'
import '@fortawesome/fontawesome-free/css/all.css'
import 'animate.css/animate.css'
import 'bulma-steps/dist/css/bulma-steps.min.css'
import VuePersist from 'vue-persist'
import VueSocketio from 'vue-socket.io-extended'
import io from 'socket.io-client'


Vue.use(Buefy, {defaultIconPack: 'fas'});
Vue.use(Resource);
Vue.use(VuePersist);
Vue.use(VueSocketio, io('/sock'));

Vue.http.interceptors.push(req => {
  return response => {
    if (response.status == 401) {
      router.push({name: "Login"});
    }
  };
});

const base = {
  token: '',
  authorized: false,
  username: '',
  password: '',
  avatar: '',
  entry: '',
  skill: 0,
  notifications: [],
  arena: {
    // message: '',
    // id: null,
    // start: false,
    // votes: null,
  }
}

new Vue({
  router: router,
  el: '#app',
  delimiters: ["[[", "]]"],
  http: {
    root: 'http://127.0.0.1:5000/'
  },
  components: {
    App
  },
  data() {
    return {
      user: base
    }
  },
  methods: {
    reset_arena() {
      this.user.arena = { };
      this.user.entry = '';
    },
    reset_all() {
      this.user = base;
      this.$router.push({name:'Login'});
    }
  },
  sockets: {
    connect() {
      console.log("connected");
    },
    disconnect() {
      console.log("disconnected");
    }
  },
  watch: {
    'user.token': function(new_token, old) {
      console.log('setting header ' + new_token);
      Vue.http.headers.common['Authorization'] = "Bearer " + new_token;
    }
  },
  persist: ['user'],
  template: '<App/>'
});
