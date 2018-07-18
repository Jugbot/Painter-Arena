<template lang="html">
  <div class="modal-card">
    <section class="modal-card-body">
      <p class="image">
          <img :src="this.image"></img>
      </p>
    </section>
  </div>
</template>

<script>
export default {
  props: ["image"],
}
</script>

<style lang="css">
</style>
