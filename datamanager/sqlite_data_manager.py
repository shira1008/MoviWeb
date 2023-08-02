from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface
from models import db, Users, Movies, Review
import hashlib




class SQLiteDataManager(DataManagerInterface):

    def read_file(self):
        """This method is not needed for the SQLite data manager,
           so we implement an empty method body."""
        pass
    

    def to_movie_instance(self, movie_data):
        """Convert a movie dictionary to a Movies instance"""
        if isinstance(movie_data, Movies):
            return movie_data
        return Movies(**movie_data)


    def to_movie_dict(self, movie):
        """Convert a Movies instance to a dictionary"""
        if isinstance(movie, dict):
            return movie
        return movie.to_dict()


    def movies_to_dict(self, movies):
        """Convert a list of Movies objects to a list of dictionaries"""
        return [movie.to_dict() for movie in movies]


    def get_user_by_id(self, user_id):
        """Return the data of user with the given ID"""
        user = Users.query.get(user_id)
        if user:
            user_dict = user.to_dict()
            user_dict['movies'] = [movie.to_dict() for movie in user.movies]
            return user_dict
        return None
    

    def get_movie_by_id(self, movies, movie_id):
        """Get the movie object from the list of movies with the given movie_id"""
        for movie in movies:
            if movie['id'] == movie_id:
                return movie
        return None
    

    def get_all_users(self):
        """Return a list of all users"""
        users = Users.query.all()
        return users


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
    
    
    def add_movie(self, user, movie_name, director, year, rating, url, user_id):
        user_movies = user["movies"]
        movie  = self.create_movie_obj(user_movies, movie_name, director, year, rating, url, user_id)
        if movie is not None:
            # Assign the correct user ID to the movie before adding it to the database
            movie.user_id = user_id
            db.session.commit()
        return "Movie already exists in the list."
        


    def create_movie_obj(self, user_movies, movie_name, director, year, rating, url, user_id):
        """Return the movie object if not return an empty one"""
        for movie in user_movies:
            if isinstance(movie, dict):
                # Handle dict data case
                if movie['name'].lower() == movie_name.lower():
                    return None
            else:
                # Handle SQLite data case
                if movie.name.lower() == movie_name.lower():
                    return None

        new_movie = Movies(
            name=movie_name.capitalize(),
            director=director,
            year=year,
            rating=rating,
            url=url,
            user_id=user_id,
        )

        # Add the new movie to the database
        db.session.add(new_movie)
        db.session.commit()

        return new_movie
    

    def update_movie_details(self, movie, movie_name, director, year, rating):
        """Update the details of the given movie"""
        if isinstance(movie, dict):  # JSON data case
            # In the JSON data case, we need to update the dictionary
            movie.update({
                "name": movie_name,
                "director": director,
                "year": year,
                "rating": rating
            })
            # Find and update the movie object in the database (if exists)
            movie_obj = Movies.query.get(movie['id'])
            if movie_obj:
                movie_obj.name = movie_name
                movie_obj.director = director
                movie_obj.year = year
                movie_obj.rating = rating
                db.session.commit()
        
        
        
    def delete_movie(self, user_id, movie_id):
        """Delete a movie from the user's movie list."""
        user = Users.query.get(user_id)
        if user:
            user_movies = user.movies
            movie_to_delete = next((movie for movie in user_movies if movie.id == movie_id), None)
            if movie_to_delete:
                user.movies.remove(movie_to_delete)
                db.session.delete(movie_to_delete)
                db.session.commit()
                db.session.commit()



    def update_user_movies(self, user_id, movies):
        user = Users.query.get(user_id)
        try:
            if user:
                if isinstance(movies[0], dict):  # dictionary data case 
                    # convert dictionaries to Movie objects
                    movies = [self.to_movie_instance(movie) for movie in movies]
                    # Update the user_id attribute for each movie
                    for movie in movies:
                        movie.user_id = user_id
                else:  # SQLite data case 
                    # directly modify the attributes of the Movies instance
                    # Update the user_id attribute for each movie
                    for movie in movies:
                        if movie.user_id != user_id:
                            movie.user_id = user_id

                user.movies = movies
                print("Updated user movies:", [movie.to_dict() for movie in movies])
                db.session.commit()
        except Exception as e:
            print(e)



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
          
        }
    

    def add_review(self, user_id, movie_id, review_text, rating):
        """Add a review for a movie"""
        user = Users.query.get(user_id)
        movie = Movies.query.get(movie_id)

        if user and movie:
            # Check if a review already exists for the user and movie
            existing_review = Review.query.filter_by(user_id=user_id, movie_id=movie_id).first()

            if existing_review:
                # Update the existing review
                existing_review.review_text = review_text
                existing_review.rating = rating
                db.session.commit()
                return existing_review
            else:
                # Create a new Review object
                new_review = Review(
                    user_id=user_id,
                    movie_id=movie_id,
                    review_text=review_text,
                    rating=rating
                )
                db.session.add(new_review)
                db.session.commit()
                return new_review

        return None


    
    def delete_review(self, user_id, movie_id):
        """Delete a review for a specific user and movie"""
        review = Review.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if review:
            db.session.delete(review)
            db.session.commit()


    def get_movie_reviews(self, user_id=None, movie_id=None):
        """Get all reviews for a specific user and/or movie"""
        query = Review.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if movie_id:
            query = query.filter_by(movie_id=movie_id)

        reviews = query.all()
        return reviews