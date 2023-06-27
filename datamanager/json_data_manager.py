import json
from datamanager.data_manager_interface import DataManagerInterface


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
    
    def get_all_users(self):
        """Return a list of all users""" 
        data = self.read_file()
        users_list = [user["name"] for user in data]
        return users_list

    def get_user_movies(self, user_id):
        """Return a list of movies for the given user ID"""
        data = self.read_file()
        for user in data:
            if user["id"] == user_id:
                return user["movies"]
        return []
            
        

