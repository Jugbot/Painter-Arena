<template lang="html">
  <div>
    <section class="hero is-fullheight is-info">

      <section class="hero-head">
        <nav class="level is-mobile box is-radiusless is-paddingless">
          <div class="level-left">
            <div class="level-item">
              <button class="avatar" @click="enterProfile()">
                <avatar :username="$root.user.username" :src="$root.user.avatar" :rounded='false'></avatar>
              </button>
            </div>
            <div class="level-item has-text-grey ">
              <span class='has-text-weight-light'> u/ </span>
              <span class="is-uppercase"> {{ $root.user.username }} </span>
            </div>
          </div>
          <div class="level-item is-hidden-mobile">
            <span class="is-size-4">Painter Arena</span>
          </div>
          <div class="level-right">
            <div class="level-item">
              <b-dropdown position="is-bottom-left">
                <button class="button is-white is-rounded" slot='trigger' @click='update_notifications()'>
                  <span class="icon">
                    <i class="far fa-bell fa-lg"></i>
                    <b-tag rounded
                    type='is-danger'
                    v-if='this.$root.user.notifications.length'>
                      {{this.$root.user.notifications.length}}
                    </b-tag>
                  </span>
                </button>
                <b-dropdown-item custom v-if='$root.user.notifications.length == 0' class="has-text-grey-light has-text-centered	">
                  Nothing here!
                </b-dropdown-item>
                <b-dropdown-item v-for='(item, index) in $root.user.notifications' :key='index'>
                  <b-message :type="types[item.type]" has-icon>
                      {{item.message}}
                  </b-message>
                </b-dropdown-item>
              </b-dropdown>
            </div>
          </div>
        </nav>
      </section>

      <section class="hero-body" style="align-items: normal;">
        <!-- <keep-alive> -->
          <router-view/>
        <!-- </keep-alive> -->
      </section>

      <section class="hero-foot">
      </section>

    </section>
  </div>
</template>

<script>
import Avatar from 'components/Avatar';

export default {
  name: "Main-Page",
  data() {
    return {
      types: {
        0: 'is-info',
        1: 'is-success',
        2: 'is-warning',
        3: 'is-danger'
      }
    }
  },
  methods: {
    enterProfile() {
      this.$router.push({
        name: "Profile",
        params: {'id': this.$root.user.username}
      });
    },
    update_notifications() {
      this.$http.get('api/u/' + this.$root.user.username, {'params': {'items': ['notifications']}}).then(response => {
        this.$root.user.notifications = response.body.notifications;
        console.log(response.body);
      });
    },
    // SOCKETS
    new_notification(data) {
      console.log("notif get!");
      this.$root.user.notifications.unshift(data);
    },
    arena_end() {
      console.log("arena end");
    }
  },
  created() {
    if (this.$root.user.username) {
      this.$router.push({
        name: "Profile",
        params: {'id': this.$root.user.username}
      });
    } else {
      console.log("Profile nonexistent, please log in.")
      this.$router.push({name: "Login"});
    }
    this.$options.sockets.new_notification = this.new_notification;
    this.$options.sockets.arena_end = this.arena_end;
  },
  beforeDestroy() {
    delete this.$options.sockets.new_notification;
    delete this.$options.sockets.arena_end;
  },
  components: {
    Avatar
  }

}
</script>

<style scoped lang="css">
  .tag {
    position: absolute;
    left: calc(100% - 1em);
    bottom: -0.5em;
    font-size: .5625rem;
    line-height: .375rem;
  }

  .dropdown-item {
    white-space: normal;
    padding-bottom: 1rem;
  }

  .button.is-white {
    color: inherit;
  }
  .header {
    width: 100vw;
  }
  .avatar {
    padding: 0;
    cursor: pointer;
    border:none;
    margin-right: 0.5em;
  }
</style>
