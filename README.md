# MoviWeb

The MoviWeb App is a Flask-based web application that allows users to track their favorite movies. Users can create an account, log in, add movies to their list, update movie details, and delete movies from their list. The application also integrates with an external API to fetch movie data, including the director, year, rating, and poster image. This App allows users to switch between different databases. Specifically, the app support both JSON-based storage (data.json) and SQLite-based storage (moviwebapp.sqlite).

## Features

- User Registration: Users can create an account by providing a unique username, password, and profile picture URL.

- User Login: Existing users can log in using their username and password.

- User Profile: Each user has a profile page that displays their username and profile picture.

- Movie List: Users can view their list of favorite movies, including the movie name, director, year, rating, and poster image.

- Add Movie: Users can search for movies using the external API and add them to their list by providing the movie name.

- Update Movie: Users can update the details of a movie in their list, including the movie name, director, year, and rating.

- Delete Movie: Users can remove a movie from their list.

## File Structure

- `app.py`: Main entry point of the application.
- `config.py`: Containing the API key.
- `datamanager/`: Directory containing the data manager module.
- `datamanager/json_data_manager.py`: Module for managing data stored in JSON format.
- `datamanager/sqlite_data_manager.py`: Module for managing data stored in database - sqlite.
- `fetching_from_api.py`: Module for fetching movie data from an external API.
- `templates/`: Directory containing HTML templates used for rendering the web pages.
- `static/`: Directory containing static files, such as CSS stylesheets and images.
- `data.json`: json file for storing user and movie data - the user can switch between databases.
- `moviwebapp.sqlite`: storing user and movie data -  - the user can switch between databases.

##  Accessing the deployed app
http://shirashahar.pythonanywhere.com



