import Vue from 'vue';
import Resource from 'vue-resource'
import App from './App';
import router from './router';

Vue.use(Resource);

Vue.mixin({ //globals
  delimiters: ["[[", "]]"],
  http: {
    root: 'http://127.0.0.1:5000/'
  },
  data: function() {
    return {
      user: {
        username: 'username',
        password: 'password'
      },
      http: {
        root: 'http://127.0.0.1:5000/'
      }
    }
  }
});

new Vue({
  router: router,
  el: '#app',
  components: {
    App
  },
  template: '<App/>'
});
