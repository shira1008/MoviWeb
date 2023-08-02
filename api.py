# api.py
from flask import Blueprint, jsonify, request
from datamanager.json_data_manager import JSONDataManager
from datamanager.sqlite_data_manager import SQLiteDataManager

api = Blueprint('api', __name__)

# data_manager = JSONDataManager('data.json')
data_manager = SQLiteDataManager()

# the endpoint is api/users:
# http://127.0.0.1:5000/api/users

@api.route('/users', methods=['GET'])
def get_users():
    """ Get all the users """
    try:
        users =  data_manager.get_all_users()
        user_list = [user.to_dict(include_pass = False) for user in users]
        return jsonify(user_list)
    except Exception as e:
        # Handle the exception and return an error response
        return jsonify({'error': str(e)}), 500


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """ Get all the movies for a user id"""
    try:
        users_movie = data_manager.get_user_movies(user_id)

        if not users_movie:
            return jsonify({'error': 'user does not exist'}), 404
        
        return jsonify(users_movie)
    except Exception as e:
        # Handle the exception and return an error response
        return jsonify({'error': str(e)}), 500


@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    """ Add a new movie by user id """
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'user does not exist'}), 404

    request_data = request.get_json()
    movie_name = request_data.get('movie_name')
    director = request_data.get('director')
    year = request_data.get('year')
    rating = request_data.get('rating')
    url = request_data.get('url')

    # Check if any required field is missing
    if not (movie_name and director and rating and url):
        return jsonify({'error': 'Missing required data'}), 400

    # Convert year and rating to the appropriate data types
    try:
        if year:
            year = int(year)
        rating = float(rating)
    except ValueError:
        return jsonify({'error': 'Invalid data types for year or rating'}), 400
    
    data_manager.add_movie(user, movie_name, director, year, rating, url, user_id)
    return jsonify({'message': 'Movie added successfully'}), 201  # Return a 201 status code for successful creation


@api.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(user_id, movie_id):
    """ Delete a movie """

    # Check if the user exists
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if the movie id exists 
    movies = data_manager.get_user_movies(user_id)
    movie = data_manager.get_movie_by_id(movies, movie_id)
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404

    # Call the data_manager to delete the movie
    data_manager.delete_movie(user_id, movie_id)
    return jsonify({'message': 'Movie deleted successfully'}), 200


