from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from datamanager.json_data_manager import JSONDataManager
from datamanager.sqlite_data_manager import SQLiteDataManager
from fetching_from_api import fetch_data
from api import api  # Importing the API blueprint
from models import db
import hashlib
import secrets
import os


# to crate a secret key
secret = secrets.token_hex(16)

app = Flask(__name__)
app.secret_key = secret
app.register_blueprint(api, url_prefix='/api')  # Registering the blueprint

current_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_directory, 'data', 'moviwebapp.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)
# data_manager = JSONDataManager('data.json')
data_manager = SQLiteDataManager()


@app.route('/')
def home():
    """ Return the index.html -> home page"""
    return render_template('index.html', user=session.get('user'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Route for the user login form 
    the session object is used to store the authenticated user's information after successful login
    """
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = data_manager.authenticate_user(name, password)

        if user:
            # Store the authenticated user's information in the session
            session['user'] = user

            # Check the type of user object and access the ID attribute accordingly
            if isinstance(user, dict):  # JSON data case
                user_id = user['id']
            else:  # SQLite data case
                user_id = user.id

            return redirect(url_for('favorite_movies', user_id=user_id))
        else:
            return render_template('login.html', error='Invalid name or password')
    return render_template('login.html', user=session.get('user'))



@app.route('/users')
def list_users():
    """ Return the users page that display the users """
    users = data_manager.get_all_users()
    
    return render_template('users.html', users=users, user=session.get('user'))

@app.route('/users/<int:user_id>')
def favorite_movies(user_id):
    """ Return the page with the favorite movie of a user """
    # Check if the user is authenticated
    if 'user' in session:
        user = session['user']
        authenticated_user_id = user['id']

        # Check if the authenticated user is accessing their own movies
        if user_id == authenticated_user_id:
            movies = data_manager.get_user_movies(user_id)
            user = data_manager.get_user_by_id(user_id)
            
            if not user:
                abort(404, "User not found.")
            user_name = user["name"]


            return render_template('user_movies.html', movies=movies, user_id=user_id, user_name=user_name, user=session.get('user'))
        else:
            # Redirect to an login page if the user is trying to access other users' movies
            return redirect('/login')  

    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('/login')



@app.route('/add_user', methods=['GET','POST'])
def add_user():
    """ Add a new user to the app """
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        profile_picture_url = request.form.get('profile_picture_url')
        
        if not data_manager.add_new_user(name, password, profile_picture_url):
            return render_template('add_user.html', error='User already exists')
        
        return redirect(url_for('list_users'))
        
    return render_template('add_user.html')


@app.route('/add_movie/<int:user_id>', methods=['POST'])
# CHECK HERE FOR THE JSON MANAGER ***********************
def add_movie(user_id):
    """ Add a new movie to the app from the API """
    movie_name = request.form.get('movie_name')
    # Fetching the data
    movie_data = fetch_data(movie_name)

    if 'Response' in movie_data and movie_data['Response'] == 'False' and movie_data['Error'] == 'Movie not found!':
        return "Movie not found in the API."
    
    user = data_manager.get_user_by_id(user_id)
    # Extract relevant information from the API response
    director = movie_data.get('Director', '')
    url = movie_data["Poster"]
    year_str = movie_data.get('Year', '')
    try:
        year = int(year_str)
    except ValueError:
        # Handle the case where the year value is not a valid integer
        year = 0  
    rating_str = movie_data.get('imdbRating', '')
    try:
        rating = float(rating_str)
    except ValueError:
        rating = 0.0

    if user:
        data_manager.add_movie(user, movie_name, director, year, rating, url, user_id)

        return redirect(url_for('favorite_movies', user_id=user_id))
    else:
        return "User not found."



@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """ Update a movie, u can update the name, rating, year, director"""
    #check the user
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found."
    
    # Retrieve the user's movies
    user_movies = data_manager.get_user_movies(user_id)
    movie = data_manager.get_movie_by_id(user_movies, movie_id)

    if not movie:
        abort(404, "Movie not found.")
            
    if request.method == "POST":
        movie_name = request.form.get('movie_name')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')

        #check the rating value
        if rating !=  "N/A":
            if float(rating) > 10 or float(rating) < 0 : 
                return "Please enter a value between 0-10"
            
        data_manager.update_movie_details(movie, movie_name, director, year, rating)
        data_manager.update_user_movies(user_id, user_movies)
        return redirect(url_for('favorite_movies', user_id=user_id))

    return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie=movie)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    """ Handle the delete movie"""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        abort(404, "User not found.")

    if isinstance(data_manager, SQLiteDataManager):

        user_movies = data_manager.get_user_movies(user_id)
        movie = data_manager.get_movie_by_id(user_movies, movie_id)

        if not movie:
            abort(404, "Movie not found.")
    
        data_manager.delete_movie(user_id, movie_id)
    else:
        # Handle the case for other data managers (e.g., JSONDataManager)
        user_movies = user['movies']
        movie_found = False
        for movie in user_movies:
            if movie['id'] == movie_id:
                print(f"Deleting movie: {movie}")
                user_movies.remove(movie)
                movie_found = True
                break
    
        if not movie_found:
            abort(404, "Movie not found.")
    
        data_manager.update_user_movies(user_id, user_movies)

    return redirect(url_for('favorite_movies', user_id=user_id))


# Route for logout
@app.route('/logout')
def logout():
    """ Remove the user information from the session"""
    session.pop('user', None)
    # Redirect to home page
    return redirect('/')


@app.route("/user/<int:user_id>/<string:username>")
def profile_page(user_id, username):
    """ Route for the profile page"""

    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))

    user = data_manager.get_user_by_id(user_id)

    if user:
        # Retrieve the profile picture URL
        profile_picture_url = user.get("profile_picture_url", "")

        # Render the template with the user and profile picture URL
        return render_template("profile.html", user=user, profile_picture_url=profile_picture_url, current_id = user_id)
    else:
        # Handle the case where the user does not exist
        return "User not found"


@app.route('/update_profile_pic', methods=['GET', 'POST'])
def update_profile_pic():
    """ Route for updating the profile pic url"""

     # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Handle the GET request
        # Render the form for uploading the profile picture
        return render_template('edit_profile_pic.html', user=session.get('user'))

    if request.method == 'POST':
        # Handle the POST request
        profile_picture_url = request.form.get('profile_picture_url')
        if not profile_picture_url:
            flash('No profile picture URL provided')
            return redirect(url_for('update_profile_pic'))

        # Update the user's profile picture URL in the data store
        user_id = session['user']['id']
        data_manager.update_user_profile_picture(user_id, profile_picture_url)

      
        return redirect(url_for('profile_page', username=session['user']['name'],  user_id = user_id))


@app.route('/add_review/<int:user_id>/<int:movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    # Retrieve the user's movies
    user_movies = data_manager.get_user_movies(user_id)
    movie = data_manager.get_movie_by_id(user_movies, movie_id)

    if not movie:
        abort(404, "Movie not found.")
            
    if request.method == "POST":
        review_text = request.form.get('review_text')
        review_rating = request.form.get('rating')

        # Check the rating value
        if review_rating !=  "N/A":
            if float(review_rating) > 10 or float(review_rating) < 0 : 
                return "Please enter a value between 0-10"

        # Add the review using the data manager
        data_manager.add_review(user_id, movie_id, review_text, float(review_rating))

        return redirect(url_for('add_review', user_id=user_id, movie_id = movie_id))

    # Fetch the user's review for the specific movie
    user_review = data_manager.get_movie_reviews(user_id, movie_id)

    return render_template('add_review.html', user_id=user_id, movie_id=movie_id, movie=movie, user_review=user_review,  user=session.get('user'))


@app.route('/delete_review/<int:user_id>/<int:movie_id>', methods=['POST'])
def delete_review(user_id, movie_id):
    # Check if the user is authenticated
    if 'user' not in session:
        return redirect(url_for('login'))

    # Check if the user is authorized to delete the review
    if session['user']['id'] != user_id:
        abort(403, "You are not authorized to delete this review.")

    # Delete the review using the data manager
    data_manager.delete_review(user_id, movie_id)

    return redirect(url_for('add_review', user_id=user_id, movie_id = movie_id))



@app.errorhandler(404)
def page_not_found(e):
    """ Return an html page for the 404 error"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)