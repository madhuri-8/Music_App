<template>
  <div>
    <h1>Login</h1>

    <form @submit.prevent="login">
      <label for="email">Email:</label>
      <input v-model="loginDetails.email" type="email" id="email" required /><br />

      <label for="password">Password:</label>
      <input v-model="loginDetails.password" type="password" id="password" required /><br />

      <label for="role">Role:</label>
      <select v-model="loginDetails.role" id="role" required>
        <option value="User">User</option>
        <option value="Creator">Creator</option>
        <option value="Admin">Admin</option>
      </select><br />

      <button type="submit">Login</button>
    </form>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      loginDetails: {
        email: "",
        password: "",
        role: "user",
      },
    };
  },
  methods: {
    async login() {
      const data = {
        email: this.loginDetails.email,
        password: this.loginDetails.password,
        role: this.loginDetails.role,
      };

      try {
        const response = await axios.post("http://localhost:5000/login_details", data);

        if (response.status === 200 && response.data.token) {
          
          localStorage.setItem("token", response.data.token);
          localStorage.setItem("role", response.data.role);
          
          switch (response.data.role) {
            case "User":
              this.$router.push("/albums");
              break;
            case "Creator":
              this.$router.push("/creatorhome"); 
              break;
            case "Admin":
              this.$router.push("/admin");
              break;
            default:
              break;
          }

          alert("Login successful!");
        } else {
          console.error("Unsuccessful login:", response);

        
          this.loginDetails.email = "";
          this.loginDetails.password = "";
          this.loginDetails.role = "user";
      
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          this.loginDetails.email = "";
          this.loginDetails.password = "";
          this.loginDetails.role = "user";
          alert("Invalid credentials");
      } 
      else {
        
        console.error("Error during login:", error);
      }
      }
    },
  },
};
</script>

<style scoped>
  /* Add your custom styles here */
  body {
    background-color: #d0dbf7; /* Choose your desired background color */
    margin: 0; /* Remove default body margin */
    font-family: 'Arial', sans-serif; /* Add a default font family if needed */
  }

  div {
    background-color: #b4e6e5; /* Choose your desired background color */
    padding: 20px; /* Add padding for better visual appearance */
    border-radius: 8px; /* Add border-radius for rounded corners */
    max-width: 400px; /* Set a maximum width to control the form's width */
    margin: auto; /* Center the form horizontally */
    margin-top: 50px; /* Add margin from the top for spacing */
  }

  form {
    display: flex;
    flex-direction: column;
  }

  label {
    margin-bottom: 8px;
  }

  input, select, button {
    margin-bottom: 12px;
    padding: 8px;
  }
</style>
