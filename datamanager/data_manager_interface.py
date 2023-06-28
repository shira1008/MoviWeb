from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    @abstractmethod
    def read_file(self):
        """Read and return the contents of the data file."""
        pass 
    
    @abstractmethod
    def get_all_users(self):
        """Return a list of all users."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Return a list of movies for the given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of movies associated with the user ID.
        """
        pass

    @abstractmethod
    def update_user_movies(self, user_id, movies):
        """Update the movie list for the given user ID.

        Args:
            user_id (int): The ID of the user.
            movies (list): The updated list of movies.
        """
        pass
    
    @abstractmethod
    def add_new_user(self, user):
        """Add a new user with an empty movie list.

        Args:
            user (str): The name of the user.
        """
        pass
