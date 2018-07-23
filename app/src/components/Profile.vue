<template lang="html">
  <div class="container is-fluid">
    <section class="section">
      <div class="level">
        <div class="level-item">
          <div class="container">
            <avatar :username="$root.user.username" :src="$root.user.avatar" :size="256" :rounded='false'></avatar>
            {{$root.user.avatar}}
          </div>
        </div>
        <div class="level-item">
          <h1 class="is-size-1 has-text-weight-bold">Rating: {{$root.user.skill}}</h1>
        </div>
      </div>
    </section>

    <section>

    </section>
  </div>
</template>

<script>
import Avatar from 'components/Avatar';

export default {
  name: "User-Profile",
  components: {
    Avatar
  },
  created() {
  }
}
</script>

<style lang="css">
</style>
