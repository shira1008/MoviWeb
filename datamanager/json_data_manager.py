import json
from datamanager.data_manager_interface import DataManagerInterface
import hashlib


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        """Read and return the contents of the JSON file"""
        try:
            with open(self.filename, "r") as handle:
                data = json.load(handle)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {str(e)}")
            return None
        
    def write_file(self, data):
        """Write the given data to the JSON file"""
        try:
            with open(self.filename, "w") as handle:
                json.dump(data, handle)
            print("File written successfully.")
        except IOError as e:
            print(f"Error writing to JSON file: {str(e)}")


    def get_user_by_id(self, user_id):
        """Return the data of user with the given ID"""
        data = self.read_file()
        for user in data:
            if user['id'] == user_id:
                return user
        return None
    
    def get_movie_by_id(self, user_movies, movie_id):
        """Return the data of a movie with the given ID"""
        for movie in user_movies:
            if movie['id'] == movie_id:
                return movie
        return None
    
    def generate_user_id(self, data):
        """Generate a unique user ID for a new user"""
        user_ids = [user["id"] for user in data]
        if user_ids:
            return max(user_ids) + 1
        else:
            return 1
        
    def generate_movie_id(self, movies):
        """Generate a unique movie ID for a new movie"""
        movie_ids = [movie['id'] for movie in movies]
        if movie_ids:
            return max(movie_ids) + 1
        else:
            return 1


    def get_all_users(self):
        """Return a list of all users""" 
        data = self.read_file()
        return data

    def get_user_movies(self, user_id):
        """Return a list of movies for the given user ID"""
        data = self.read_file()
        # print("Data:", data)  # Check the value of data
        for user in data:
            if user["id"] == user_id:
                return user["movies"]
        return []

            
    def add_new_user(self, user, password, profile_picture_url):
        """Add a new user with an empty movie list"""
        data = self.read_file()
        if user.lower() in [d["name"].lower() for d in data] :
            print("User already exist") 
            return False # User already exists

        # Generate a unique ID for the new user
        user_id = self.generate_user_id(data)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
    

        # Create the new user entry
        new_user = {
            "id": user_id,
            "name": user,
            'password': hashed_password,
            'profile_picture_url':profile_picture_url,
            "movies": []
        }

        # Add the new user to the data
        data.append(new_user)

        # Write the updated data to the file
        try:
            with open(self.filename, "w") as handle:
                json.dump(data, handle)
            print("User added successfully.")
        except IOError as e:
            print(f"Error adding user: {str(e)}")
        return True

    def add_movie(self,user, movie_name, director, year, rating, url, user_id):
        user_movies = user['movies']
        movie = self.create_movie_obj(user_movies, movie_name,director,year,rating,url)
        if len(movie) > 0 :
            user_movies.append(movie)
        else:
            return "Movie already exists in the list."
        self.update_user_movies(user_id, user_movies)


    def create_movie_obj(self, user_movies, movie_name,director,year,rating,url):
        """Return the movie object if not return an empty one"""
        for movie in user_movies:
            if movie['name'] == movie_name.capitalize():
                return {}
        
        new_movie_id = self.generate_movie_id(user_movies)
        movie = {
            'id': new_movie_id,
            'name': movie_name.capitalize(),
            'director': director,
            'year': year,
            'rating':rating,
            'url': url
        }
        return movie
    
    def update_movie_details(self, movie, movie_name, director, year, rating):
        """updating the movie details"""
        movie['name'] = movie_name
        movie['director'] = director
        movie['year'] = year
        movie['rating'] = rating


    def update_user_movies(self, user_id, movies):
        """Update the movie list after adding or update or delete the movie for the given user ID"""
        data = self.read_file()
        for user in data:
            if user['id'] == user_id:
                user['movies'] = movies
                
        # Write the updated data to the file
        self.write_file(data)
        

    def update_user_profile_picture(self, user_id, profile_picture_url):
        """Update the profile picture URL for the user with the given ID"""
        data = self.read_file()
        for user in data:
            if user['id'] == user_id:
                user['profile_picture_url'] = profile_picture_url
                break
        
        # Write the updated data to the file
        self.write_file(data)


    def authenticate_user(self, name, password):
        """ Authenticate a user based on the provided name and password"""
        users = self.get_all_users()

        for user in users:
            if user['name'] == name:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if user['password'] == hashed_password:
                    return user
        return None
