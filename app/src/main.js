import Vue from 'vue';
import Resource from 'vue-resource'
import App from 'App';
import router from 'router/index';

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
