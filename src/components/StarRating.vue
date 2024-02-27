<template>
  <div class="star-rating">
    <span v-for="star in stars" :key="star" @click="selectRating(star)">
      ⭐️
    </span>
  </div>
</template>

<script>
export default {
  data() {
    return {
      stars: [1, 2, 3, 4, 5],
    };
  },
  methods: {
    selectRating(selectedRating) {
      // Emit the selected rating to the parent component
      this.$emit('rating-selected', selectedRating);
    },
  },
};
</script>

<style scoped>
.star-rating {
  font-size: 24px;
}
</style>
