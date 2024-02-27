<template>
  <div class="creator-home">
    <div class="header">
      <h2>Creator Home</h2>
      <!-- User Dashboard Button -->
      <router-link to="/albums" class="user-dashboard-button">User Dashboard</router-link>
      <!-- Logout Button -->
      <button @click="logout" class="logout-button">Logout</button>
    </div>

    <!-- Display Albums -->
    
    
    <div v-for="album in albums" :key="album.album_id" class="album-card-link">
      <!-- Album Details -->
      <p>Album ID: {{ album.album_id }}</p>
      <p>Album Name: {{ album.album_name }}</p>
      <p>Year of Release: {{ album.year_of_release }}</p>
      <router-link :to="'/albums/' + album.album_id">
      <button class="action-button">Songs</button>
      </router-link>
      <!-- Edit Album Button -->
      <button @click="toggleEditForm(album)" class="action-button">Edit Album</button>

      <!-- Delete Album Button -->
      <button @click="deleteAlbum(album.album_id)" class="action-button">Delete Album</button>
    </div>
  

    <!-- Edit Album Form -->
    <form v-if="isEditingAlbum" @submit.prevent="saveChanges" class="album-form">
      <h3>Edit Album</h3>
      <label for="editedAlbumName">Album Name:</label>
      <input v-model="editedAlbumName" type="text" id="editedAlbumName" required />

      <label for="editedYearOfRelease">Year of Release:</label>
      <input v-model="editedYearOfRelease" type="number" id="editedYearOfRelease" required />

      <label for="editedGenre">Genre :</label>
      <input v-model="editedGenre" type="text" id="editedGenre" required />

      <label for="editedImageName">Image Name:</label>
      <input v-model="editedImageName" type="text" id="editedImageName" required />

      <div class="form-buttons">
        <button type="submit">Save Changes</button>
        <button @click="cancelEdit" type="button">Cancel</button>
      </div>
    </form>

    <!-- Add New Album Form -->
    <form v-if="isAddingAlbum" @submit.prevent="addNewAlbum" class="album-form" enctype="multipart/form-data">
  <h3>Add New Album</h3>
  <label for="newAlbumName">Album Name:</label>
  <input v-model="newAlbumName" type="text" id="newAlbumName" name="album_name" required />

  <label for="newYearOfRelease">Year of Release:</label>
  <input v-model="newYearOfRelease" type="number" id="newYearOfRelease" name="year_of_release" required />

  <label for="newImageName">Image Name:</label>
  <input v-model="newImageName" type="text" id="newImageName" name="image" required />

  <label for="albumImage">Album Image:</label>
  <input type="file" ref="albumImage" @change="handleImageChange" accept="image/*" name="albumImage" required />

  <label for="genre"> Genre : </label>
  <input v-model="genre" type="text" id="genre" name="genre" required/>

  <div class="form-buttons">
    <button type="submit">Add Album</button>
    <button @click="cancelAdd" type="button">Cancel</button>
  </div>
</form>


    <!-- Add Album Button -->
    <button @click="startAddingAlbum" class="action-button add-album-button">Add Album</button>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      albums: [],
      newAlbumName: "",
      newYearOfRelease: null,
      newImageName: "",
      genre:"",
      isEditingAlbum: false,
      isAddingAlbum: false,
      editingAlbumId: null,
      editedAlbumName: "",
      editedYearOfRelease: null,
      editedGenre:"",
      editedImageName: "",
      newImage: null,
    };
  },
  methods: {
    async fetchCreatorAlbums() {
      try {
        const response = await axios.get("http://localhost:5000/creatorhome", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        this.albums = response.data.albums;
      } catch (error) {
        console.log("Error fetching creator albums:", error);
      }
    },

    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },

    toggleEditForm(album) {
      this.isEditingAlbum = !this.isEditingAlbum;
      this.isAddingAlbum = false; // Close add new album form
      this.editingAlbumId = album.album_id;

      if (this.isEditingAlbum) {
        this.fetchAlbumDetails(album.album_id);
      } else {
        this.clearEditFields();
      }
    },
    

    handleImageChange(event) {
        const fileInput = event.target;
        if (fileInput.files.length > 0) {
            this.newImage = fileInput.files[0];
        }
    },

    async fetchAlbumDetails() {
      try {
        const response = await axios.get(`http://localhost:5000/creatorhome`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        const albumDetails = response.data.album;
        this.editedAlbumName = albumDetails.album_name;
        this.editedYearOfRelease = albumDetails.year_of_release;
        this.editedGenre = albumDetails.genre;
        this.editedImageName = albumDetails.image;
      } catch (error) {
        console.log("Error fetching album details:", error);
      }
    },

    async saveChanges() {
      try {
        await axios.put(
          `http://localhost:5000/creatorhome/${this.editingAlbumId}`,
          {
            album_name: this.editedAlbumName,
            year_of_release: this.editedYearOfRelease,
            image: this.editedImageName,
            genre: this.editedGenre,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );

        this.isEditingAlbum = false;
        this.editingAlbumId = null;

        this.$router.push("/creatorhome");
      } catch (error) {
        console.log("Error saving changes:", error);
      }
    },

    cancelEdit() {
      this.isEditingAlbum = false;
      this.editingAlbumId = null;
      this.clearEditFields();
    },

    async deleteAlbum(albumId) {
      try {
        const token = localStorage.getItem("token");
        await axios.delete(`http://localhost:5000/creatorhome/${albumId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.fetchCreatorAlbums();
        console.log("Album Deleted:", albumId);
      } catch (error) {
        console.log("Error deleting album:", error);
      }
    },

    startAddingAlbum() {
      this.isAddingAlbum = true;
      this.isEditingAlbum = false; // Close edit album form
      this.clearNewAlbumFields();
    },

    async addNewAlbum() {
    try {
        // Create a FormData object
        const formData = new FormData();
        formData.append('album_name', this.newAlbumName);
        formData.append('year_of_release', this.newYearOfRelease);
        formData.append('image', this.newImageName);
        formData.append('genre', this.genre);
        formData.append('albumImage', this.$refs.albumImage.files[0]); // Assuming albumImage is a file input
        // Make API request to add the album
        await axios.post(
            "http://localhost:5000/creatorhome",
            formData,
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                    'Content-Type': 'multipart/form-data',
                },
            }
        );

        this.clearNewAlbumFields();
        this.fetchCreatorAlbums();
        console.log("New Album Added");
    } catch (error) {
        console.log("Error adding new album:", error);
    }
},


    cancelAdd() {
      this.isAddingAlbum = false;
      this.clearNewAlbumFields();
    },

    clearEditFields() {
      this.editedAlbumName = "";
      this.editedYearOfRelease = null;
      this.editedImageName = "";
    },

    clearNewAlbumFields() {
      this.newAlbumName = "";
      this.newYearOfRelease = null;
      this.newImageName = "";
    },
  },

  mounted() {
    this.fetchCreatorAlbums();
  },
};
</script>
<style scoped>
.creator-home {
  max-width: 800px;
  margin: 0 auto;
}

.header {
  background-color: #3498db;
  color: #fff;
  padding: 10px;
  text-align: center;
}

.user-dashboard-button,
.logout-button {
  background-color: #2ecc71;
  color: #fff;
  padding: 8px 16px;
  border: none;
  margin: 0 5px;
  text-decoration: none;
  cursor: pointer;
}

.album-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  margin-top: 20px;
}

.album-card {
  background-color: #ecf0f1;
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin: 10px;
  padding: 15px;
}

.album-details {
  margin-bottom: 10px;
}

.album-buttons {
  display: flex;
  justify-content: space-around;
}

.action-button {
  background-color: #3498db;
  color: #fff;
  padding: 8px 16px;
  border: none;
  cursor: pointer;
}

.add-album-button {
  background-color: #2ecc71;
}

.album-form {
  background-color: #ecf0f1;
  padding: 15px;
  margin-top: 20px;
  border-radius: 10px;
}

.form-buttons {
  margin-top: 15px;
}

.form-buttons button {
  margin-right: 10px;
}
</style>