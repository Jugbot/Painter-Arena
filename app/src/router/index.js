import Vue from 'vue';
import Router from 'vue-router';
import Login from '@/components/Login'
import Arena from '@/components/Arena'
import Main from '@/components/Main'

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      redirect: () => {
        return { //TODO: store credentials somehow?
          name: 'Login'
        };
      }
    },
    {
      path: '/u/:id',
      name: 'Main',
      component: Main
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    }
  ],
  mode: 'hash'
});
