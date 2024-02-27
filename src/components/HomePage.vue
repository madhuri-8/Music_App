<template>
  <div class="hello">
    <h1>Welcome to Swara</h1>
    <img alt="Veena" src="@/assets/Veena.png" class="app-image">
    <p>
      Swara is your gateway to a diverse world of music. From classical melodies in Karnatic and Hindustani traditions to the beats of pop and rock genres, Swara brings you a curated collection of soul-soothing tunes. Explore, discover, and immerse yourself in the rich tapestry of musical experiences.
    </p>
    <router-link to="/login_details" class="nav-link">Login</router-link>
    <router-link to="/signup" class="nav-link">Signup</router-link>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
};
</script>

<style scoped>
.hello {
  background-color: #ffe8cc; /* Light peach background color */
  padding: 40px;
  text-align: center;
}

h1 {
  margin-top: 20px;
  font-size: 36px;
  color: #333;
}

.app-image {
  max-width: 100%;
  height: auto;
  margin: 20px 0;
}

p {
  font-size: 18px;
  line-height: 1.6;
  color: #555;
}

.nav-link {
  display: inline-block;
  margin: 20px 10px;
  padding: 15px 30px;
  text-decoration: none;
  color: #fff;
  background-color: #ff9900; /* Orange color for the button */
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.nav-link:hover {
  background-color: #e68a00; /* Darker orange color on hover */
}
</style>
