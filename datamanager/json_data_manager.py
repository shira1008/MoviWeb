import json
from datamanager.data_manager_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_user_by_id(self, user_id):
        """Return the data of user with the given ID"""
        data = self.read_file()
        for user in data:
            if user['id'] == user_id:
                return user
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

    def read_file(self):
        """Read and return the contents of the JSON file"""
        try:
            with open(self.filename, "r") as handle:
                data = json.load(handle)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {str(e)}")
            return None
    
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

            
    def add_new_user(self, user):
        """Add a new user with an empty movie list"""
        data = self.read_file()

        # Generate a unique ID for the new user
        user_id = self.generate_user_id(data)

        # Create the new user entry
        new_user = {
            "id": user_id,
            "name": user,
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


    def update_user_movies(self, user_id, movies):
        """Update the movie list after adding or update or delete the movie for the given user ID"""
        data = self.read_file()
        for user in data:
            if user['id'] == user_id:
                user['movies'] = movies
                
        # Write the updated data to the file
        try:
            with open(self.filename, 'w') as handle:
                json.dump(data, handle)
            print('User movies updated successfully.')
        except IOError as e:
            print(f'Error updating user movies: {str(e)}')
        




