import json
from data_manager_interface import DataManagerInterface

class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_all_users(self):
        """Return a list of all users""" 
        with open(self.filename, "r") as handle:
            users = json.load(handle)
        users_list = [user["name"] for user in users]
        return users_list

    def get_user_movies(self, user_id):
        # Return a list of all movies for a given user
        pass


useres_obj = JSONDataManager("data.json")
print(useres_obj.get_all_users())