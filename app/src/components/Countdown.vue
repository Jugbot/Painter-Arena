<template lang="html">
  <span class="">
    <div>{{ days | digit_formatter }}</div>:<div>{{ hours | digit_formatter }}</div>:<div>{{ minutes | digit_formatter }}</div>:<div>{{ seconds | digit_formatter }}</div>
  </span>
</template>

<script>
export default {
  name: "countdown",
  props : {
    date : {
      type: String
    }
  },

  data() {
    return {
      now: Math.trunc((new Date()).getTime() / 1000)
    }
  },
  computed: {
    timestamp() {
      if (!this.date)
        return 0;
      return Math.trunc(Date.parse(this.date) / 1000);
    },

    timedelta() {
      var delta = this.timestamp - this.now;
      if (delta < 0) {
        this.$emit('timeout');
        return 0;
      }
      return delta
    },

    seconds() {
      return (this.timedelta) % 60;
    },

    minutes() {
      return Math.trunc((this.timedelta) / 60) % 60;
    },

    hours() {
      return Math.trunc((this.timedelta) / 60 / 60) % 24;
    },

    days() {
      return Math.trunc((this.timedelta) / 60 / 60 / 24);
    }
  },
  mounted() {
    window.setInterval(() => {
      this.now = Math.trunc((new Date()).getTime() / 1000);
    },1000);
  },
  filters: {
    digit_formatter(value) {
      if (!value) return '00'
      value = value.toString()
      if(value.toString().length <= 1)
        return "0"+value.toString();
      return value.toString();
    }
  }
}
</script>

<style scoped lang="css">
  div {
    display: inline-block;
    width: 2em;
  }
</style>

// http://fareez.info/blog/countdown-timer-using-vuejs/
