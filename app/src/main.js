import Vue from 'vue'
import Resource from 'vue-resource'
import App from 'App'
import router from 'router/index'
import BootstrapVue from 'bootstrap-vue'

import Buefy from 'buefy'
import 'buefy/lib/buefy.css'
import '@fortawesome/fontawesome-free/css/all.css'

Vue.use(Buefy, {defaultIconPack: 'fas'})

Vue.use(Resource);

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
        authorized: false,
        username: '',
        password: '',
        avatar: '',
        entry: '',
        skill: '',
        arena: {
          id: '',
          start: false,
          votes: '',
        }
      }
    }
  },
  template: '<App/>'
});
