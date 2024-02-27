<template>
    <div>
      <h2>Signup</h2>
      <router-link to="/" class="back-button">Back</router-link>
      <form @submit.prevent="handleSubmit" class="signup-form">
        <label for="people_name">Name:</label>
        <input v-model="formData.people_name" type="text" required>
  
        <label for="role">Role:</label>
        <select v-model="formData.role" required class="role-select">
          <option value="" disabled>Select Role</option>
          <option value="Creator">Creator</option>
          <option value="User">User</option>
        </select>
  
        <label for="password">Password:</label>
        <input v-model="formData.password" type="password" required>
  
        <label for="email">Email:</label>
        <input v-model="formData.email" type="email" required>
  
        <button type="submit">Signup</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  export default {
    name: 'SignUp',
    data() {
      return {
        formData: {
          people_name: "",
          role: "",
          password: "",
          email: "",
        },
      };
    },
    methods: {
      handleSubmit() {
        // Assuming you use an HTTP library like Axios to make the request
        axios.post("http://localhost:5000/signup", this.formData)
          .then(response => {
            console.log(response.data.message);
            // Handle success, e.g., redirect to login page
            this.$router.push({ path: '/', query: { successMessage: 'Successfully signed up!' } });
          })
          .catch(error => {
            console.log("Signup error:",error);
            // Handle error, e.g., display error message to the user
          });
      },
    },
  };
  </script>
  
  <style scoped>
/* Your styles go here */
.signup-form {
  max-width: 400px;
  margin: 0 auto;
}

label {
  display: block;
  margin-bottom: 8px;
}

input,
select,
button {
  width: 100%;
  padding: 8px;
  margin-bottom: 16px;
}

button {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: #45a049;
}
.back-button {
  margin-bottom: 16px;
  display: inline-block;
  padding: 8px 16px;
  background-color: #007bff;
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.back-button:hover {
  background-color: #0056b3;
}

.role-select {
  width: 105%; /* Adjust the width as needed */
}
</style>
  