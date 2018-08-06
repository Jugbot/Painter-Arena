<template lang="html">
    <form action="">
        <div class="modal-card" style="width: auto">
            <header class="modal-card-head">
                <p class="modal-card-title has-text-centered">Custom Arena</p>
            </header>
            <section class="modal-card-body">
                <b-field label="max players">
                    <b-input
                        type="number"
                        v-model="max_players"
                        min="2"
                        max="20"
                        placeholder="10">
                    </b-input>
                </b-field>

                <b-field label="expiration">
                  <b-timepicker
                      inline
                      :min-time='mintime'
                      v-model="timeout_delta">
                  </b-timepicker>
                </b-field>

                <b-field label="prompt">
                  <b-input
                      type='text'
                      v-model="prompt"
                      placeholder="(random)">
                  </b-input>
                </b-field>
            </section>
            <footer class="modal-card-foot">
                <button class="button is-primary is-fullwidth" @click='submit()'>Go</button>
            </footer>
        </div>
    </form>
</template>

<script>
export default {
  name: "arena-controls-modal",
  data() {
    const min = new Date(0);
    min.setHours(0);
    min.setMinutes(1);
    return {
      max_players: null,
      timeout_delta: new Date(min),
      prompt: null,
      mintime: min
    }
  },
  computed: {
    settings() {
      return {
        'max_players': parseInt(this.max_players),
        //zero day compensation add 19 hours...
        'timeout_delta': this.timeout_delta.getTime() + 19 * 3600000,
        'prompt': this.prompt
      }
    }
  },
  methods: {
    submit() {
      this.$emit('submit', this.settings);
      this.$parent.close();
    }
  }

}
</script>

<style lang="css">
</style>
