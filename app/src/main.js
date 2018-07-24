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
// Vue.use(VuePersist);
Vue.use(VueSocketio, io('/sock'));

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
      user: {
        token: null,
        authorized: false,
        username: '',
        password: '',
        avatar: '',
        entry: '',
        skill: '',
        notifications: [],
        arena: {
          id: '',
          start: false,
          votes: '',
        }
      }
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
  // persist: ['token'],
  template: '<App/>'
});
