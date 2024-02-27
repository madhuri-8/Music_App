import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/components/HomePage.vue';
import AlbumDisplay from '@/components/AlbumDisplay.vue';
import SongDisplay from '@/components/SongDisplay.vue';
import AdminDetails from '@/components/AdminDetails.vue';
import LoginDetails from '@/components/LoginDetails.vue'; // Add the import for the login component
import CreatorHome from '@/components/CreatorHome.vue';
import PlayList from '@/components/PlayList.vue';
import StarRating from '@/components/StarRating.vue';
import SignUp from '@/components/SignUp.vue';

const routes = [
  { path: '/', component: HomePage },
  { path: '/albums', component: AlbumDisplay },
  { path: '/albums/:album_id', component: SongDisplay, props: true },
  { path: '/admin', component: AdminDetails },
  { path: '/login_details', component: LoginDetails },
  { path: '/creatorhome', component: CreatorHome },
  {path: '/playlist', component: PlayList},
  {path: '/api/song/ratings', component: StarRating},
  {path: '/signup', component: SignUp}


];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
