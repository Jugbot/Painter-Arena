import Vue from 'vue'
import Resource from 'vue-resource'
import App from 'App'
import router from 'router/index'
import BootstrapVue from 'bootstrap-vue'

import Buefy from 'buefy'
import 'buefy/lib/buefy.css'

Vue.use(Buefy)

// import 'bootstrap/dist/css/bootstrap.css'
// import 'bootstrap-vue/dist/bootstrap-vue.css'
// Vue.use(BootstrapVue);

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
        avatar: false,
        entry: false,
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
