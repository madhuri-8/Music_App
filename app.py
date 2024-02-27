import os
from flask import Flask , jsonify
from flask_restful import Api, Resource,request
from flask_sqlalchemy import SQLAlchemy
from flask import make_response
from sqlalchemy import func
from datetime import datetime,timedelta
from flask_bcrypt import Bcrypt
from flask_cors import CORS 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
current_dir = os.path.abspath(os.path.dirname(__file__))
from flask_caching import Cache
from workers import create_celery_app
from celery.schedules import crontab
from task import send_email,send_report

app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(current_dir,"api_music.sqlite3")
app.config["JWT_SECRET_KEY"] = "your-secret-key"

db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
cel_app=create_celery_app(app)
####################################    CACHE     ##############################
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6381/0'  
app.config['CACHE_OPTIONS'] = {'DEBUG': False}
cache = Cache()
cache.init_app(app)

#################################    DATABASE    ##################################

class People(db.Model):
    people_id = db.Column(db.Integer(),primary_key=True)
    people_name= db.Column(db.String(), nullable=False)
    people_signup_date = db.Column(db.Date(),nullable=False) 
    role = db.Column(db.String(),nullable= False) 
    password = db.Column(db.String(),nullable=False)
    email=db.Column(db.String(),nullable=False)
    visited_time = db.Column(db.DateTime(), default=datetime.utcnow)

class Album(db.Model):
    album_id = db.Column(db.Integer(), primary_key=True)
    album_name = db.Column(db.String(), nullable=False,unique=True)
    image = db.Column(db.String()) ##### path to the image ####
    year_of_release = db.Column(db.String(),nullable=False)
    genre = db.Column(db.String,nullable=False)
    songs = db.relationship('Song', backref="album")
    album_creator = db.Column(db.Integer(),db.ForeignKey('people.people_id'))
    album_creator_name = db.relationship('People', foreign_keys=[album_creator])

class Song(db.Model):
    song_id = db.Column(db.Integer(), primary_key=True)
    song_name = db.Column(db.Integer(), nullable= False)
    lyrics = db.Column(db.String(),nullable=False)
    song_date = db.Column(db.Date(),nullable=False)
    song_mp3 = db.Column(db.String(),nullable=False)
    album_song = db.Column(db.Integer(), db.ForeignKey('album.album_id'))
    times_played = db.Column(db.Integer())  ### store number of time song is played ##

class Playlist(db.Model):
    playlist_id = db.Column(db.Integer(),primary_key=True)
    owner = db.Column(db.Integer(),db.ForeignKey('people.people_id')) ## owner of playlist ##
    songs_list = db.Column(db.JSON)

class Rating(db.Model):
    rating_id = db.Column(db.Integer(),primary_key=True)
    ratings = db.Column(db.Integer(),nullable=False)
    song = db.Column(db.Integer(),db.ForeignKey('song.song_id'))
    user_rated = db.Column(db.Integer(),db.ForeignKey('people.people_id'))

###################################### eencryption ##############################    
def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

################################# celery tasks ##################################
def get_all_email_ids():
   
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    with app.app_context():
    
        email_ids = [person.email for person in People.query.filter(People.visited_time < twenty_four_hours_ago).all()]
        return email_ids

users = get_all_email_ids()

@cel_app.on_after_configure.connect
def setup_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task( 
        crontab(hour=16, minute=8),
        send_email_to_all_users.s(),
        name='send_email_daily_at_7pm',
    )

    sender.add_periodic_task(
        crontab(hour=16, minute=8, day_of_month=11),
        send_monthly_report_to_creators.s(),
        name='Monthly Report to Admin',
    )
@cel_app.task
def send_email_to_all_users():
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    
    users = People.query.filter(People.visited_time < twenty_four_hours_ago).all()
    
    for user in users:
        send_email(user.email)

@cel_app.task
def send_monthly_report_to_creators():
    creators = People.query.filter_by(role='Creator').all()

    for creator in creators:
        creator_report = generate_creator_report(creator)
        subject = "Monthly Creator Report"
        
        
        send_report(creator.email, 'Monthly Creator Report', creator_report)

def generate_creator_report(creator):
    report = f"<h1>Hi {creator.people_name}</h1>\n"
    report+="<h3>Here is the monthly report</h3>\n"
    report += "<hr>\n"
    albums = Album.query.filter_by(album_creator=creator.people_id).all()
    for album in albums:
        report += f"<h2>Album: {album.album_name}</h2>\n"
        songs = Song.query.filter_by(album_song=album.album_id).all()
        report += "<table border='1'>\n"
        report += "<tr><th>Song</th><th>Average Rating</th><th>Times Played</th></tr>\n"
        for song in songs:
            ratings = Rating.query.filter_by(song=song.song_id).all()
            total_ratings = sum(rating.ratings for rating in ratings)
            avg_rating = total_ratings / len(ratings) if ratings else 0
            song_info = {
                'song_name': song.song_name,
                'avg_rating': avg_rating,
                'times_played': song.times_played
            }
            report += f"<tr><td>{song_info['song_name']}</td><td>{song_info['avg_rating']}</td><td>{song_info['times_played']}</td></tr>\n"
        report += "</table>\n"
    report += "<hr>\n"
    return report

class Home(Resource):
    def get(self):
        return "Ping"

class Albums(Resource):
    def get(self):
        alb = Album.query.all()
        albums_data = []
        for albu in alb:
            album_data = {
                'album_id': albu.album_id,
                'album_name': albu.album_name,
                'year_of_release': albu.year_of_release,
                'album_image': albu.image,
                'album_creator_name': albu.album_creator_name.people_name,  # Access creator name through the relationship
                'album_genre': albu.genre,

            }
            albums_data.append(album_data)
        return jsonify(albums_data)
    
class SongDisplay(Resource):
    def get(self):
        songs = Song.query.all()
        songs_data = []
        for so in songs:
            ratings_per_song = Rating.query.filter_by(song=so.song_id).all()
            rating_list = [rating.ratings for rating in ratings_per_song]
            avg_rating = sum(rating_list) / len(rating_list) if len(rating_list) > 0 else 0

            song_data = {
                
                'song_name': so.song_name,
                'song_mp3':so.song_mp3,
                'song_album':so.album_song,
                'average_rating': avg_rating,
            }
            songs_data.append(song_data)
        return jsonify(songs_data)
    
api.add_resource(SongDisplay,'/songs')

#################### Creator functionalities #########################
class Songs(Resource):
    
    def get(self,album_id):
        s = Song.query.filter_by(album_song=album_id).all()
        a = Album.query.filter_by(album_id=album_id).first()
        song_creator = a.album_creator
        songs_data=[]
        for so in s:
            data={
                'song_id':so.song_id,
                'song_name':so.song_name,
                'lyrics':so.lyrics,
                'song_mp3':so.song_mp3,
                'song_creator':song_creator,
                
            }
            songs_data.append(data)
        
        return jsonify({'songs': songs_data, 'album_creator': song_creator})

    def post(self, album_id):
        data = request.form
        song_name = data.get('song_name')
        lyrics = data.get('lyrics')
        song_mp3 = data.get('song_mp3')
        song_date_str=data.get('song_date')
        
        song_date = datetime.strptime(song_date_str, '%Y-%m-%d').date()
        new_song = Song(song_name=song_name, lyrics=lyrics, song_mp3=song_mp3, album_song=album_id,song_date=song_date,times_played=0)

        db.session.add(new_song)
        db.session.commit()
        mp3_file = request.files.get('mp3File')
        lyrics_file = request.files.get('lyrics_File')

        if mp3_file:
            mp3_file.save(f'src/assets/Songs/{mp3_file.filename}')

        if lyrics_file:
            lyrics_file.save(f'src/assets/Songs/{lyrics_file.filename}')

        return jsonify({'message': 'Song added successfully', 'song_id': new_song.song_id})

    def put(self, album_id,song_id):
        data = request.get_json()
        song = Song.query.filter_by(song_id=song_id, album_song=album_id).first()
        song_date_str=data.get('song_date')
        
        song_date = datetime.strptime(song_date_str, '%Y-%m-%d').date()
        if song:
            song.song_name = data.get('song_name')
            song.song_date = song_date
            db.session.commit()

            return jsonify({'message': 'Song updated successfully'})
        else:
            return jsonify({'message': 'Song not found'})

    def delete(self, album_id,song_id):
        song = Song.query.filter_by(song_id=song_id).first()
        if song:

            Rating.query.filter_by(song=song_id).delete()
            playlists = Playlist.query.filter(Playlist.songs_list.contains([song_id])).all()
            for playlist in playlists:
                playlist.songs_list.remove(song_id)

            db.session.commit()
            db.session.delete(song)
            db.session.commit()
            return jsonify({'message': 'song deleted'})
        else:
            return jsonify({'message':'cant delete song'})


api.add_resource(Home, '/')
api.add_resource(Albums, '/albums')
api.add_resource(Songs,'/albums/<int:album_id>','/albums/<int:album_id>/<int:song_id>')

class Admin(Resource):
    
    def get(self):
        total_users = People.query.count()
        total_creators = People.query.filter_by(role='Creator').count()
        total_albums = Album.query.count()
        total_songs = Song.query.count()
        album_stat= Album.query.all()
        song_stat = Song.query.all()
        album_stats = [{'album_id':stat.album_id,'album_name': stat.album_name, 'genre': stat.genre} for stat in album_stat]
        song_stats=[{'song_id':stat.song_id,'song_name':stat.song_name} for stat in song_stat]
        return jsonify({
            'total_users': total_users,
            'total_creators': total_creators,
            'total_albums': total_albums,
            'total_songs': total_songs,
            'song_stats': song_stats,
            'album_stats': album_stats,
        })

api.add_resource(Admin, '/admin')

class CreatorHome(Resource):
    @jwt_required()
    @cache.cached(timeout=30)
    def get(self):
        creator_id = get_jwt_identity()
        creator_albums = Album.query.filter_by(album_creator=creator_id).all()
        creator_id = get_jwt_identity()
        creator_albums = Album.query.filter_by(album_creator=creator_id).all()
        
        albums = [
                {
                    'album_id': album.album_id,
                    'album_name': album.album_name,
                    'year_of_release': album.year_of_release,
                }
                for album in creator_albums
            ]
        return jsonify({'albums': albums})

    @jwt_required()
    def post(self):
        try:
            data = request.form
            new_album = Album(
                album_name=data['album_name'],
                year_of_release=data['year_of_release'],
                image= data['image'],
                genre=data['genre'],
                album_creator=get_jwt_identity(),
            )
            db.session.add(new_album)
            db.session.commit()

            image_file = request.files.get('albumImage')
            if image_file:
                image_file.save(f'src/assets/{image_file.filename}')
            return jsonify(
                {'message': 'Album created successfully', 'album_id': new_album.album_id})
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @jwt_required()
    def put(self, album_id):
        try:
            data = request.get_json()
            album = Album.query.filter_by(
                album_id=album_id, album_creator=get_jwt_identity()
            ).first()

            if not album:
                return jsonify(
                    {
                        'message': 'Album not found or you do not have permission to edit it'
                    }
                )

            album.album_name = data['album_name']
            album.year_of_release = data['year_of_release']
            album.image=data['image']
            album.genre=data['genre']
            db.session.commit()

            return jsonify({'message': 'Album updated successfully'})
        except Exception as e:
            return jsonify({'message': str(e)})


    @jwt_required()
    def delete(self, album_id):
        try:
            album = Album.query.filter_by(
                album_id=album_id, album_creator=get_jwt_identity()
            ).first()
            Song.query.filter_by(album_song=album.album_id).delete()
            db.session.delete(album)
            db.session.commit()

            return jsonify({'message': 'Album deleted successfully'})
        except Exception as e:
            return jsonify({'message': str(e)})
        
api.add_resource(CreatorHome,'/creatorhome','/creatorhome/<int:album_id>')

@app.route("/login_details", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role") 
    use = People.query.filter_by(email=email, role=role).first()
    if use and bcrypt.check_password_hash(use.password, password):
        use.visited_time = datetime.utcnow()
        db.session.commit()
        access_token = create_access_token(identity=use.people_id, additional_claims={"role": use.role})
        return {"token": access_token, "role": use.role}
    return {"message": "Invalid credentials"}, 401




@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route("/signup",methods=['POST'])
def signup():
    data = request.json  
    people_name = data.get('people_name')
    role = data.get('role')
    password = data.get('password')
    email = data.get('email')

    p= People.query.all()
    for peo in p:
        if peo.email == email:
            return jsonify({'message': 'Email Id already exists'})

    hashed_password = hash_password(password)
    new_person = People(
        people_name=people_name,           
        people_signup_date=datetime.utcnow().date(),
        role=role,
        password=hashed_password,
        email=email
    )

    db.session.add(new_person)
    db.session.commit()

    return jsonify({'message': 'Signup successful'})

class Playlists(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(owner=current_user_id).first()

        if not playlist:
            return {'message': 'Playlist not found'}, 404
        songs_list = playlist.songs_list if isinstance(playlist.songs_list, list) else []
        songs = Song.query.filter(Song.song_id.in_(songs_list)).all()
        serialized_songs = [
            {'song_id': song.song_id, 'song_name': song.song_name,'song_mp3':song.song_mp3,}
            for song in songs
        ]

        return {'songs': serialized_songs}
    
    @jwt_required()
    def delete(self, song_id):
        current_user_id = get_jwt_identity()

        playlist = Playlist.query.filter_by(owner=current_user_id).first()

        if not playlist:
            return {'message': 'Playlist not found'}, 404

        if song_id in playlist.songs_list:
            playlist.songs_list = [sid for sid in playlist.songs_list if sid != song_id]
            db.session.commit()
            
            return {'message': 'Song removed from playlist successfully', 'playlist_id': playlist.playlist_id}, 200
        else:
            
            return {'message': 'Song not found in the playlist'}, 404

api.add_resource(Playlists, '/playlist', '/playlist/<int:song_id>')

@app.route("/playlist/<int:user_id>/<int:song_id>",methods=["POST"])
@jwt_required()
def addtoplaylist(user_id,song_id):
    current_user_id = get_jwt_identity()

    if current_user_id != user_id:
        return {'message': 'Unauthorized access to the playlist'}, 401
    playlist = Playlist.query.filter_by(owner=user_id).first()

    if not playlist:
                        
        new_playlist = Playlist(
        owner=user_id,
        songs_list=[song_id]
        )

        db.session.add(new_playlist)
        db.session.commit()

        return {'message': 'Playlist created and song added successfully', 'playlist_id': new_playlist.playlist_id}, 201
    else:
        
        if song_id not in playlist.songs_list:
            playlist.songs_list= playlist.songs_list +[song_id]
            db.session.commit()
            
            return {'message': 'Song added to playlist successfully', 'playlist_id': playlist.playlist_id}, 200
        else:
            return {'message': 'Song already exists in the playlist', 'playlist_id': playlist.playlist_id}, 200
        

    
class SongRatingAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            ratings = data.get("ratings")
            song_id = data.get("song_id")
            user_rated = data.get("user_rated_id")

            if not all([ratings, song_id, user_rated]):
                return {"message": "Incomplete data in the request body"}, 400

            
            existing_rating = Rating.query.filter_by(song=song_id, user_rated=user_rated).first()

            if existing_rating:
                return {"message": "User has already rated the same song"}, 400

            
            rating = Rating(ratings=ratings, song=song_id, user_rated=user_rated)
            db.session.add(rating)
            db.session.commit()

            return {"message": "Rating submitted successfully"}, 200

        except Exception as e:
            
            db.session.rollback()
            return {"message": "Internal Server Error"}, 500

api.add_resource(SongRatingAPI, '/api/song/ratings')


if __name__ == "__main__":
    app.run(debug=False)
