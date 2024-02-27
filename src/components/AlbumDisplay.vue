<template>
  <div>
    <h1>Albums</h1>
    <div class="header-buttons">
      <button @click="logout">Logout</button>
      <button v-if="isCreator" @click="goToCreatorDashboard">Creator Dashboard</button>
      <button v-if="isAdmin" @click="goToAdminDashboard">Admin Dashboard</button>
      <router-link to="/playlist" class="btn btn-playlist">Playlist</router-link>

    </div>

    <!-- Search bar for albums and songs -->
    <input v-model="searchQuery" placeholder="Search albums,songs,creators, genre"/>

    <div class="album-list">
      <!-- Loop through albums and display each album -->
      <div v-for="album in filteredAlbums" :key="album.album_id" class="album-card">
        <router-link :to="'/albums/'+ album.album_id" class="album-container">
          <img :src="getAlbumImagePath(album.album_image)" alt="Album Cover" class="album-image"> 
          <div class="album-details">
            <p class="album-name">{{ album.album_name }}</p>
            <p class="album-year">{{ album.year_of_release }}</p>
            <p class="album-creator">{{ album.album_creator_name }}</p>
            <p class="album-genre">{{ album.album_genre }}</p>
          </div>
        </router-link>
      </div>
    </div>

    
    <table v-if="filteredSongs.length > 0">
      
      <thead>
        <tr>
          <th>Song Name</th>
          <th>Ratings</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="song in filteredSongs" :key="song.song_id">
          <td>{{ song.song_name }}</td>
          <td>{{ song.average_rating }}</td>
          <td>
            <button @click="togglePlayback(song)" v-if="!isPlaying(song)">Play</button>
            <button @click="togglePlayback(song)" v-if="isPlaying(song)">Pause</button>
          </td>
        </tr>
      </tbody>
    </table>
    
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AlbumDisplay',
  data() {
    return {
      apiBaseUrl: "http://localhost:5000/albums",
      albums: [],
      loggedInUserRole: null,
      searchQuery: '',
      songs: [],
      currentSong: null,
      audioPlayer: new Audio(),
    };
  },
  computed: {
    isCreator() {
      return this.loggedInUserRole === 'Creator';
    },
    isAdmin() {
      return this.loggedInUserRole === 'Admin';
    },
    filteredAlbums() {
      // Filter albums and songs based on the searchQuery
      const query = this.searchQuery.toLowerCase();
      return this.albums.filter(album =>
        album.album_name.toLowerCase().includes(query) ||
        album.album_creator_name.toLowerCase().includes(query) || // Include creator name in the filter
        album.album_genre.toLowerCase().includes(query) &&
        (album.songs && album.songs.some(song =>
          song.song_name.toLowerCase().includes(query) ||
          song.album_name.toLowerCase().includes(query)
        ))
      );
    },
    filteredSongs() {
      const query = this.searchQuery.toLowerCase();
      return this.songs.filter(song =>
        song.song_name.toLowerCase().includes(query) ||
        (song.album_name && song.album_name.toLowerCase().includes(query))
      );
    },
  },
  methods: {
    fetchAlbums() {
      axios.get(this.apiBaseUrl)
        .then(response => {
          this.albums = response.data;
          console.log("Albums received from the backend:", this.albums);
        })
        .catch(error => {
          console.error("Error fetching albums:", error);
        });
    },
    getAlbumImagePath(image) {
      return require(`@/assets/${image}.jpg`);
    },
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    getLoggedInUser() {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const tokenParts = token.split('.');
          const payload = JSON.parse(atob(tokenParts[1]));
          console.log('Logged-in user:', payload);

          const userId = payload.sub; 
          this.loggedInUserId = userId;

          const userRole = payload.role; 
          
          this.loggedInUserRole = userRole;
        
        } catch (error) {
          console.error('Error parsing token:', error);
        }
      } else {
        console.error('No token found. User not logged in.');
      }
    },
    goToCreatorDashboard() {
      this.$router.push("/creatorhome");
    },
    goToAdminDashboard() {
      this.$router.push("/admin");
    },
    fetchSongs() {
      axios.get("http://localhost:5000//songs")
        .then(response => {
          this.songs = response.data;
          console.log("Songs received from the backend:", this.songs);
        })
        .catch(error => {
          console.error("Error fetching songs:", error);
        });
    },
    togglePlayback(song) {
      if (this.currentSong && this.currentSong.song_id === song.song_id) {
        // If the clicked song is the same as the currently playing song, pause it
        this.pause();
      } else {
        // Otherwise, play the clicked song
        this.play(song);
      }
    },

    play(song) {
      if (this.currentSong) {
        // If another song is currently playing, pause it first
        this.pause();
      }

      // Set the source of the audio player to the selected song
      this.audioPlayer.src = this.getSongPath(song.song_mp3);
      this.audioPlayer.play();

      // Update the currentSong property
      this.currentSong = song;
    },

    pause() {
      // Pause the audio player
      this.audioPlayer.pause();

      // Reset the currentSong property
      this.currentSong = null;
    },

    isPlaying(song) {
      // Check if the provided song is the currently playing song
      return this.currentSong && this.currentSong.song_id === song.song_id;
    },

    getSongPath(songName) {
      return require(`@/assets/Songs/${songName}.mp3`);
    },
  },
  beforeUnmount() {
    // Stop the audio player when the component is destroyed
    this.audioPlayer.pause();
    this.audioPlayer.currentTime = 0;
  },

  async mounted() {
    this.getLoggedInUser();
    this.fetchAlbums();
    this.fetchSongs();
  },
};
</script>

<style scoped>
  /* General Styles */
  body {
    font-family: 'Arial', sans-serif;
    background-color: #f8f8f8;
    margin: 0;
    padding: 0;
  }

  /* Header Styles */
  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 20px;
  }

  .header-buttons {
    text-align: center;
    margin-bottom: 20px;
  }

  button {
    background-color: #3498db;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    margin-right: 10px;
    cursor: pointer;
  }

  /* Album Styles */
  .album-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    margin-bottom: 20px;
  }

  .album-card {
    margin: 20px;
    text-decoration: none;
    color: black;
    transition: transform 0.3s ease-in-out;
    width: 45%;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .album-card:hover {
    transform: scale(1.05);
  }

  .btn {
    background-color: #3498db;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    margin-right: 10px;
    cursor: pointer;
    text-decoration: none; /* Ensure no underline for links */
    display: inline-block; /* Make sure it behaves like a block element */
  }

  .album-container {
    border: 1px solid #ddd;
    border-radius: 10px;
    overflow: hidden;
  }

  .album-image {
    max-width: 100%;
    height: 200px;
    object-fit: cover;
  }

  .album-details {
    padding: 15px;
  }

  .album-name {
    font-size: 18px;
    margin: 0;
    color: #333;
  }

  .album-year {
    font-size: 14px;
    color: #555;
    margin: 5px 0;
  }

  .album-creator {
    font-size: 14px;
    color: #777;
    margin: 5px 0;
  }

  .album-genre{
    font-size: 14px;
    color: #777;
    margin : 5px 0;
  }

  /* Songs Styles */

  .search-bar {
    padding: 8px;
    margin-bottom: 15px;
    width: 100%;
    box-sizing: border-box;
  }

  .table-container {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }

  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }

  th {
    background-color: #f2f2f2;
  }

  .btn-play {
    background-color: #2ecc71; /* Green color, you can change it */
    /* Add more styles as needed */
  }

  .btn-pause {
    background-color: #e74c3c;
  }

  button {
    background-color: #3498db;
    color: white;
    padding: 8px 12px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  .btn-playlist {
    background-color: #2ecc71; /* Green color, you can change it */
    /* Add more styles as needed */
  }

  /* Responsive Styles */
  @media (max-width: 768px) {
    .album-card {
      width: 100%;
    }
  }
</style>