import Vue from 'vue';
import Router from 'vue-router';
import Login from 'components/Login'
import Arena from 'components/Arena'
import Main from 'components/Main'
import NotFound from 'components/NotFound'
import Profile from 'components/Profile'

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '',
      // name: 'Main',
      component: Main,
      children: [
        {
          path: '/arena/:id',
          name: 'Arena',
          component: Arena
        },
        {
          path: '/u/:id',
          name: 'Profile',
          component: Profile
        }
      ]
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/404',
      component: NotFound
    },
    {
      path: '*',
      redirect: '/404'
    },
  ],
  mode: 'hash'
});
