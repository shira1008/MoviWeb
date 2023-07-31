from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface
from models import db, Users, Movies
import hashlib



class SQLiteDataManager(DataManagerInterface):

    def read_file(self):
        """This method is not needed for the SQLite data manager,
           so we implement an empty method body."""
        pass
    
    def get_user_by_id(self, user_id):
        """Return the data of user with the given ID"""
        user = Users.query.get(user_id)
        if user:
            return user.to_dict()
        return None
    
    def get_all_users(self):
        """Return a list of all users"""
        return Users.query.all()


    def get_user_movies(self, user_id):
        """Return a list of all movies of a specific user"""
        user = Users.query.get(user_id)
        if user:
                return [movie.to_dict() for movie in user.movies]
        return []
        
            
    def add_new_user(self, user, password, profile_picture_url):
        """Add a new user to the database"""
        existing_user = Users.query.filter_by(name=user).first()
        if existing_user:
            return False  # User already exists

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = Users(name=user, password=hashed_password, profile_picture_url=profile_picture_url)
        db.session.add(new_user)
        db.session.commit()
        return True
    

    def create_movie_obj(self, user_movies, movie_name, director, year, rating, url):
        """Return the movie object if not return an empty one"""
        for movie in user_movies:
            if movie.name == movie_name.capitalize():
                return {}

        new_movie_id = self.generate_movie_id(user_movies)
        movie = Movies(id=new_movie_id, name=movie_name.capitalize(), director=director, year=year,
                       rating=rating, url=url)
        return movie
    
    
    def update_movie_details(self, movie, movie_name, director, year, rating):
        """Update the movie details"""
        movie.name = movie_name
        movie.director = director
        movie.year = year
        movie.rating = rating


    def update_user_movies(self, user_id, new_movie):
        """Update the movie list by adding a new movie for the given user ID"""
        user = Users.query.get(user_id)
        if user:
            # Get the list of user's movies as dictionary-like objects
            user_movies = [movie.to_dict() for movie in user.movies]
            # Append the new movie to the list of user's movies
            user_movies.append(new_movie.to_dict())
            # Update the user's movies in the database
            user.movies = [Movies(**movie_data) for movie_data in user_movies]
            db.session.commit()



    def update_user_profile_picture(self, user_id, profile_picture_url):
        """Update the profile picture URL for the user with the given ID"""
        user = Users.query.get(user_id)
        if user:
            user.profile_picture_url = profile_picture_url
            db.session.commit()


    def authenticate_user(self, name, password):
        """Authenticate a user based on the provided name and password"""
        user = Users.query.filter_by(name=name).first()
        if user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user.password == hashed_password:
                 return self.user_to_dict(user)
        return None
    

    def user_to_dict(self, user):
        """Convert the Users object to a dictionary representation"""
        return {
            'id': user.id,
            'name': user.name,
            'password': user.password,
            'profile_picture_url': user.profile_picture_url,
            # Add any other attributes you want to include in the dictionary representation
        }