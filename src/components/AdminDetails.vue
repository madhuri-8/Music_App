<template>
  <div class="admin-details">
    <h1>Admin Dashboard</h1>
    <button @click="logout" class="action-button logout">Logout</button>
    <button @click="UserDashBoard" class="action-button logout">User Dashboard</button>


    <div class="app-stats">
      <h2>App Statistics</h2>
      <ul>
        <li>Total Users: {{ adminDetails.total_users }}</li>
        <li>Total Creators: {{ adminDetails.total_creators }}</li>
        <li>Total Albums: {{ adminDetails.total_albums }}</li>
        <li>Total Songs: {{ adminDetails.total_songs }}</li>
      </ul>
    </div>

    <div class="performance-stats">
      <div class="album-stats">
        <h2>Albums Present</h2>
        <div class="album-list">
          <div v-for="stat in adminDetails.album_stats" :key="stat.album_id" class="album-card">
            <div class="album-container">
              <p class="album-name"> {{ stat.album_name }}</p>
              <p class="album-name"> {{ stat.genre }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="song-stats">
        <h2>Songs Present</h2>
        <div class="song-list">
          <div v-for="stat in adminDetails.song_stats" :key="stat.song_id" class="song-card">
            <div class="song-container">
              <p class="song-name"> {{ stat.song_name }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      adminDetails: {
        total_users: 0,
        total_creators: 0,
        total_albums: 0,
        total_songs: 0,
        album_stats: [],
        song_stats: [],
      },
    };
  },
  mounted() {
    this.fetchAdminDetails();
  },
  methods: {
    fetchAdminDetails() {
      // Replace 'your_backend_url' with the actual URL of your backend
      fetch('http://localhost:5000/admin')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.adminDetails = data;
          console.log("Admin details",this.adminDetails);
        })
        .catch(error => {
          console.error('Error fetching admin details:', error);
        });
    },
    UserDashBoard(){
      this.$router.push("/albums");
    },
    async logout() {
      try {
        // Get the token from localStorage
        const token = localStorage.getItem('token');
        console.log('Token:', token);

        // Make a request to the backend /logout endpoint with the token in the headers
        const response = await axios.post('http://localhost:5000/logout', {}, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // Handle the response as needed
        console.log(response.data.message); // Assuming the backend sends a message

        // Clear the token from localStorage
        localStorage.removeItem('token');

        // Redirect to the login page or perform any other desired action
        this.$router.push('/');
      } catch (error) {
        console.error('Error during logout:', error);
      }
    },
  },
};
</script>

<style scoped>
.admin-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color:rgb(231, 234, 211);
}

h1 {
  font-size: 28px;
  margin-bottom: 20px;
}

.action-button {
  text-decoration: none;
  padding: 10px 20px;
  color: white;
  background-color: #3498db; /* Blue color, change as needed */
  border-radius: 5px;
  margin-right: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #2980b9; /* Darker shade of blue on hover, change as needed */
}

.logout {
  background-color: #e74c3c; /* Red color for logout button, change as needed */
}

.user-dashboard-button {
  background-color: #2ecc71; /* Green color for user dashboard button, change as needed */
}

.app-stats, .performance-stats {
  margin-bottom: 30px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  font-size: 16px;
  margin-bottom: 10px;
}

.album-list, .song-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

.album-card, .song-card {
  margin: 20px;
  text-decoration: none;
  color: black;
  transition: transform 0.3s ease-in-out;
  width: 45%;
}

.album-card:hover, .song-card:hover {
  transform: scale(1.05);
}

.album-container, .song-container {
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #f5f5f5;
  text-align: center;
  padding: 15px;
}
</style>
