<template>
  <div>
    <h1>My Music</h1>
    <button class="btn" @click="goToAlbums">Back</button>
    <button class="btn" @click="logout">Logout</button>
    <button class="btn go-to-playlist" @click="goToPlaylist">Go to Playlist</button>

    <section class="player">
      <h2 class="song-title">{{ current.song_name }} </h2>
      <div class="controls">
        <button class="btn prev" @click="prev" v-show="songs.length > 0">Prev</button>
        <button class="btn play" v-if="!isPlaying && songs.length > 0" @click="play">Play</button>
        <button class="btn pause" v-if="isPlaying && songs.length > 0" @click="pause">Pause</button>
        <button class="btn next" @click="next" v-show="songs.length > 0">Next</button>
      </div>
      <div class="lyrics" v-if="currentLyrics && songs.length > 0">
        <h3>Lyrics</h3>
        <pre>{{ currentLyrics }}</pre>
      </div>
      <p v-else-if="songs.length > 0">No lyrics available</p>
    </section>

    <section class="playlist" v-if="songs.length > 0">
      <div v-for="song in songs" :key="song.song_id" class="song-item">
        <div class="song-info">
          <h3>{{ song.song_name }}</h3>
        </div>
        <div class="song-actions">
          <button class="btn" @click="() => play(song)">Play</button>
          <button class="btn" @click="addToPlaylist(song)">Add to Playlist</button>


          <button class="btn" @click="showRatingModal(song)">Rate</button>

            <!-- Rating modal -->
            <div v-if="showRatingModalFlag" class="modal">
              <div class="modal-content">
                <h3>Rate "{{ current.song_name }}"</h3>
                <star-rating @rating-selected="saveRating" />
                <button class="btn" @click="closeRatingModal">Close</button>
              </div>
            </div>  

      

          <template v-if="isCreator">
            <button class="btn" @click="() => toggleEditForm(song)" v-if="isAlbumCreator(song.song_creator)">Edit</button>
            <button class="btn" @click="deleteSong(song.song_id)" v-if="isAlbumCreator(song.song_creator)">Delete</button>
            <form v-if="showEditForm" @submit.prevent="editSong(song)" class="edit-form">
              <h3>Edit Song</h3>
              <div class="form-group">
                <label for="song_name">Song Name:</label>
                <input v-model="editedSong.song_name" type="text" required>
              </div>
              <div class="form-group">
                <label for="song_date">Release Date:</label>
                <input v-model="editedSong.song_date" type="date" required>
              </div>
              <button type="submit" class="btn update-btn">Update Song</button>
            </form>
          </template>
        </div>
      </div>
    </section>

    <p v-else>No songs in the album</p>

    <div>
      <button v-if="isCreator && isAlbum()" class="btn" @click="toggleAddSongForm">Add to Album</button>
      <form v-if="isCreator && showAddSongForm" @submit.prevent="addSongToAlbum" class="add-song-form">
        
        <h3>Add Song to Album</h3>
      <label for="song_name">Song Name:</label>
      <input v-model="newSong.song_name" type="text" required>

      <label for="lyrics">Lyrics:</label>
      <input v-model="newSong.lyrics" type="text" required>

      <label for="song_mp3">Song File Name:</label>
      <input v-model="newSong.song_mp3" type="text" required>

      <label for="song_date">Release Date:</label>
      <input v-model="newSong.song_date" type="date" required>

      <label for="mp3File">MP3 File:</label>
      <input type="file" id="mp3File" accept=".mp3" @change="handleFileUpload">

      <label for="lyricsFile">Lyrics File:</label>
      <input type="file" id="lyricsFile" accept=".txt" @change="handleFileUpload">

      <button type="submit" class="btn">Add Song</button>
    </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import StarRating from '@/components/StarRating.vue';

export default {
  name: 'app',
  data() {
    return {
      current: {},
      index: 0,
      isPlaying: false,
      songs: [],
      loggedInUserRole: null,
      currentLyrics: null,
      player: new Audio(),
      albumCreator: null,

      showAddSongForm: false,
      selectedFile: null,
      newSong: {
        song_name: '',
        lyrics: '',
        song_mp3: null,
        song_date: '',
      },


      showEditForm: false,
      editedSong: {
        song_name: '',
        song_date: '',
      },
      showRatingModalFlag: false,
      apiBaseUrl: 'http://localhost:5000', // Update with your actual API base URL
    };
  },
  components: {
    StarRating,
  },
  computed: {
    isCreator() {
      return this.loggedInUserRole === 'Creator';
    },
  },
  methods: {

    play(song) {
      if (typeof song.song_mp3 !== 'undefined') {
        this.current = song;
        this.player.src = this.getSongPath(song.song_mp3);
        this.fetchLyrics(song.lyrics);
      }

      this.player.play().then(() => {
        this.isPlaying = true;
      }).catch((error) => {
        console.error('Error playing audio:', error);
        this.isPlaying = false;
      });

      // Clear any existing 'ended' event listeners
      this.player.removeEventListener('ended', this.onSongEnd);

      // Add the new 'ended' event listener
      this.player.addEventListener('ended', this.onSongEnd);
    },

    pause() {
      this.player.pause();
      this.isPlaying = false;
    },

    next() {
      this.index++;
      if (this.index > this.songs.length - 1) {
        this.index = 0;
      }

      this.current = this.songs[this.index];
      this.fetchLyrics(this.current.lyrics);
      this.play(this.current);
    },

    prev() {
      this.index--;
      if (this.index < 0) {
        this.index = this.songs.length - 1;
      }

      this.current = this.songs[this.index];
      this.fetchLyrics(this.current.lyrics);
      this.play(this.current);
    },

    getSongPath(songName) {
      return require(`@/assets/Songs/${songName}.mp3`);
    },

    fetchLyrics(lyricsPath) {
      if (lyricsPath) {
        const lyricsFileName = `${lyricsPath}.txt`;

        // Use static import instead of dynamic require
        import(`@/assets/Songs/${lyricsFileName}`)
          .then(({ default: lyricsContent }) => {
            this.currentLyrics = lyricsContent;
          })
          .catch((error) => {
            console.log('Error fetching lyrics:', error);
            this.currentLyrics = null;
          });
      } else {
        this.currentLyrics = null;
      } 
    
    },

    onSongEnd() {
      // Reset isPlaying flag
      this.isPlaying = false;

      // Only proceed to the next song if it was playing
      if (this.isPlaying) {
        this.index++;
        if (this.index > this.songs.length - 1) {
          this.index = 0;
        }

        this.current = this.songs[this.index];
        this.fetchLyrics(this.current.lyrics);

        // Wait for a short duration before starting the next song
        setTimeout(() => {
          this.play(this.current);
        }, 1000);

        // Add the new 'ended' event listener
        this.player.addEventListener('ended', this.onSongEnd);
      }
    },

    fetchSongs() {
      const albumId = this.$route.params.album_id;
      axios
        .get(`${this.apiBaseUrl}/albums/${albumId}`)
        .then((response) => {
          //this.songs = response.data;
          const { songs, album_creator } = response.data;

      // Now you have access to both songs and song_creator
          this.songs = songs;
          this.albumCreator = album_creator;
          console.log("albumcreator",this.albumCreator)

        })
        .catch((error) => {
          console.error('Error fetching songs:', error);
        });
    },

    goToAlbums() {
      this.$router.push('/albums');
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
        const userId = payload.sub; // Use 'sub' to get the user ID
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
isAlbumCreator(creator_id) {
    
    return creator_id === this.loggedInUserId;
  },

isAlbum(){
  console.log("userId", this.loggedInUserId);
  console.log("albumCreator", this.albumCreator)
  return this.albumCreator === this.loggedInUserId;
  
},

addToPlaylist(song) {
    this.getLoggedInUser();

    const userId = this.loggedInUserId;
    const songId = song.song_id;
    console.log(userId,songId)
    const token = localStorage.getItem('token');
    console.log('Token:', token);

    // Make API request to add the song to the playlist
    axios.post(`${this.apiBaseUrl}/playlist/${userId}/${songId}`, {}, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
      .then((response) => {
        // Assuming your backend returns a message and playlist ID
        console.log(response.data.message);
        console.log('Updated Playlist ID:', response.data.playlist_id);

      })
      .catch((error) => {
        console.error('Error adding song to playlist:', error);
      });
  },

  goToPlaylist() {
      this.$router.push('/playlist');
    },



    /////////////////////// ADDING SONG LOGIC //////////////////////////
    toggleAddSongForm() {
      this.showAddSongForm = !this.showAddSongForm;
    },

    addSongToAlbum() {
    const album_id = this.$route.params.album_id;
    const formData = new FormData();
    formData.append('song_name', this.newSong.song_name);
    formData.append('lyrics', this.newSong.lyrics);
    formData.append('song_date', this.newSong.song_date);
    formData.append('song_mp3', this.newSong.song_mp3);
    formData.append('lyrics_File', this.selectedLyricsFile);
    formData.append('mp3File', this.selectedFile); // Append the selected file

    axios.post(`${this.apiBaseUrl}/albums/${album_id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
    .then((response) => {
      console.log(response.data.message);
      this.showAddSongForm = false;
      this.fetchSongs();
    })
    .catch((error) => {
      console.error('Error adding song to album:', error);
    });
  },

  handleFileUpload(event) {
  const fileInput = event.target;
  const fieldName = fileInput.id;

  if (fileInput.files.length > 0) {
    if (fieldName === 'mp3File') {
      this.selectedFile = fileInput.files[0];
    } else if (fieldName === 'lyricsFile') {
      this.selectedLyricsFile = fileInput.files[0];
    }
  }
},


////////////////////////////////////// Editing Form /////////////////////////////
    toggleEditForm(song) {
       //Set the initial values in the edit form
      this.editedSong = {
        song_name: song.song_name,
        song_date: song.song_date,
      };
      this.showEditForm = !this.showEditForm;
    },

    editSong(song) {
  console.log('Editing song:', song);
  const album_id = this.$route.params.album_id;

  axios.put(`${this.apiBaseUrl}/albums/${album_id}/${song.song_id}`, {
    song_name: this.editedSong.song_name,
    song_date: this.editedSong.song_date,
  })
  .then((response) => {
    console.log(response.data.message);
    this.showEditForm = false;
    this.fetchSongs();
  })
  .catch((error) => {
    console.error('Error updating song:', error);
  });
},



//////////////////////////////////Deleting Song ////////////////////////////
    deleteSong(songId) {
      const albumId = this.$route.params.album_id;

      axios.delete(`${this.apiBaseUrl}/albums/${albumId}/${songId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })
        .then((response) => {
          console.log(response.data.message);

          this.fetchSongs();
        })
        .catch((error) => {
          console.log('Error deleting song:', error);
        });
    },
    
//////////////////////////////////// RATING MODEL ////////////////////////////
    showRatingModal(song) {
      // Set the current song and show the modal
      this.current = song;
      this.showRatingModalFlag = true;
    },

    closeRatingModal() {
      // Close the rating modal
      this.showRatingModalFlag = false;
    },

    saveRating(selectedRating) {
  // Handle the selected rating (e.g., send it to the server)
  console.log(`Rating for "${this.current.song_name}": ${selectedRating}`);

  // Send the rating to the backend
  const songId = this.current.song_id;
  const userId = this.loggedInUserId; // Assuming you have the user ID
  const token = localStorage.getItem('token');

  axios.post(`${this.apiBaseUrl}/api/song/ratings`,
    {
      ratings: selectedRating,
      song_id: songId,
      user_rated_id: userId,
    },
    {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    }
  )
    .then((response) => {
      console.log(response.data.message);
    })
    .catch((error) => {
      console.log('Error submitting rating:', error);
    });

  // Close the modal after saving the rating
  this.closeRatingModal();
},
  },


  beforeUnmount() {
    // Ensure the player is paused and reset when the component is destroyed
    this.player.pause();
    this.player.currentTime = 0;
    this.isPlaying = false;
  },

  beforeRouteLeave(to, from, next) {
    // Check if the player is currently playing
    if (this.isPlaying) {
      // Pause the player when leaving the route
      this.player.pause();
      this.isPlaying = false;
    }
    next();
  },

  created() {
    this.fetchSongs();
  },
  async mounted() {
    this.getLoggedInUser();
  },
};
</script>

<style scoped>
/* Add your aesthetic styling here */
.btn {
  padding: 8px 12px;
  margin-right: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.song-item {
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

.player {
  margin-top: 20px;
  padding: 20px;
  background-color: #333;
  color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.player h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.player .controls {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
}

.player button {
  padding: 10px 20px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.lyrics {
  margin-top: 20px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.lyrics h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.lyrics pre {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  color: #555;
}

.lyrics p {
  font-size: 14px;
  line-height: 1.5;
  color: #555;
}


.btn {
  padding: 8px 12px;
  margin-right: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Add your existing styles here */

.edit-form {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

.update-btn {
  background-color: #2196F3; /* Change color to suit your design */
}
</style>
