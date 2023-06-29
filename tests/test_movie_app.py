import sys
import os
import pytest

# Add the project's root directory to the module search path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datamanager.json_data_manager import JSONDataManager


def test_generate_user_id():
    data_manager = JSONDataManager("test_data.json")

    # Test generating a unique user ID with an empty data list
    data = []
    user_id = data_manager.generate_user_id(data)
    assert user_id == 1

    # Test generating a unique user ID with existing data
    data = [
        {"id": 1, "name": "Alice", "movies": []},
        {"id": 2, "name": "Bob", "movies": []}
    ]
    user_id = data_manager.generate_user_id(data)
    assert user_id == 3


def test_get_user_movies():
    # Create test data
    test_data = [
        {"id": 1, "name": "Alice", "movies": ["Movie 1", "Movie 2"]},
        {"id": 2, "name": "Bob", "movies": ["Movie 3", "Movie 4"]}
    ]

    data_manager = JSONDataManager("test_data.json")

    # Set the test data in the JSONDataManager
    data_manager.read_file = lambda: test_data

    # Test getting movies for a specific user ID
    movies = data_manager.get_user_movies(1)
    assert movies == ["Movie 1", "Movie 2"]

    # Test getting movies for a non-existent user ID
    movies = data_manager.get_user_movies(3)
    assert movies == []


def test_add_new_user():
    data_manager = JSONDataManager("test_data.json")
    initial_user_count = len(data_manager.get_all_users())

    # Add a new user
    data_manager.add_new_user("John Doe")

    # Verify that the user count has incremented by 1
    updated_user_count = len(data_manager.get_all_users())
    assert updated_user_count == initial_user_count + 1


if __name__ == "__main__":
    pytest.main([__file__])