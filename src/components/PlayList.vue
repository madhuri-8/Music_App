<template>
  <div>
    <h1>Playlist</h1>
    <button class="btn btn-logout" @click="logout">Logout</button>
    <router-link to="/albums" class="btn btn-dashboard">User Dashboard</router-link>

    <div v-for="song in playlist" :key="song.song_id" class="playlist-item">
      <div class="song-info">
        <h3>{{ song.song_name }}</h3>
      </div>
      <div class="song-actions">
        <button class="btn btn-play" @click="play(song)">Play</button>
        <button class="btn btn-pause" @click="pause">Pause</button>
        <button class="btn btn-remove" @click="removeSong(song.song_id)">Remove</button>
      </div>
    </div>

    <p v-if="playlist.length === 0">No songs in the playlist</p>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        playlist: [],
        isPlaying: false,
        player: new Audio(),
        apiBaseUrl: 'http://localhost:5000', // Update with your actual API base URL
      };
    },
    methods: {
      play(song) {
        if (typeof song.song_mp3 !== 'undefined') {
          this.player.src = this.getSongPath(song.song_mp3);
        }
  
        this.player.play().then(() => {
          this.isPlaying = true;
        }).catch((error) => {
          console.error('Error playing audio:', error);
          this.isPlaying = false;
        });
      },
  
      pause() {
        this.player.pause();
        this.isPlaying = false;
      },
  
      removeSong(songId) {
        const token = localStorage.getItem('token');
        axios.delete(`${this.apiBaseUrl}/playlist/${songId}`,{
            headers: {
            Authorization: `Bearer ${token}`,
            },
        })
          .then((response) => {
            console.log(response.data.message);
            // Update the playlist after removing the song
            this.fetchPlaylist();
          })
          .catch((error) => {
            console.error('Error removing song from playlist:', error);
          });
      },
  
      fetchPlaylist() {
        // Make API request to fetch the user's playlist
        
        
        const token = localStorage.getItem('token');

        axios.get(`${this.apiBaseUrl}/playlist`, {
            headers: {
            Authorization: `Bearer ${token}`,
            },
        }).then((response) => {
            this.playlist = response.data.songs;
          })
          .catch((error) => {
            console.error('Error fetching playlist:', error);
          });
      },
  
      getSongPath(songName) {
        return require(`@/assets/Songs/${songName}.mp3`);
      },
      
     
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    },
  
    created() {
      // Fetch the playlist when the component is created
      this.fetchPlaylist();
    },
  
    beforeUnmount() {
      // Cleanup logic if needed
      this.player.pause();
      this.player.currentTime = 0;
      this.isPlaying = false;
    },
  };
  </script>
  
  <style scoped>
  /* Add your styling for the playlist items and buttons */
  .playlist-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .song-info {
    flex: 1;
  }
  
  .song-actions {
    display: flex;
    gap: 10px;
  }

  .playlist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.song-info {
  flex: 1;
}

.song-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-logout {
  background-color: #e74c3c; /* Red color */
  color: white;
}

.btn-dashboard {
  background-color: #3498db; /* Blue color */
  color: white;
}

.btn-play {
  background-color: #2ecc71; /* Green color */
  color: white;
}

.btn-pause {
  background-color: #f39c12; /* Yellow color */
  color: white;
}

.btn-remove {
  background-color: #e74c3c; /* Red color */
  color: white;
}
  </style>
  