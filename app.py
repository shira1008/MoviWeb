from flask import Flask, render_template, request, redirect, url_for, abort,session
from datamanager.json_data_manager import JSONDataManager
from fetching_from_api import fetch_data
import hashlib
import secrets

secret = secrets.token_hex(16)

app = Flask(__name__)
app.secret_key = secret
data_manager = JSONDataManager('data.json')

def authenticate_user(name, password):
    """Authenticate a user based on the provided name and password"""
    users = data_manager.get_all_users()

    for user in users:
        if user['name'] == name:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['password'] == hashed_password:
                return user
    return None


@app.route('/')
def home():
    """ Return the index.html -> home page"""
    return render_template('index.html')

# Route for the user login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = authenticate_user(name, password)
        if user:
            # Store the authenticated user's information in the session
            session['user'] = user
            return redirect(url_for('favorite_movies', user_id=user['id']))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/users')
def list_users():
    """ Return the users page that display the users """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def favorite_movies(user_id):
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
            return render_template('user_movies.html', movies=movies, user_id=user_id, user_name=user_name)
        else:
            # Redirect to an appropriate page if the user is trying to access other users' movies
            return redirect('/login')  # You can customize the redirection destination as per your requirement - here i should able accses for a profile

    else:
        # Redirect to the login page if the user is not authenticated
        return redirect('/login')



@app.route('/add_user', methods=['GET','POST'])
def add_user():
    """ Add a new user to the app """
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        
        if not data_manager.add_new_user(name, password):
            return render_template('add_user.html', error='User already exists')
        
        return redirect(url_for('list_users'))
        
    return render_template('add_user.html')


@app.route('/add_movie/<int:user_id>', methods=['POST'])
def add_movie(user_id):
    """ Add a new movie to the app form the api """
    movie_name = request.form.get('movie_name')
    #fetching the data
    movie_data = fetch_data(movie_name)
    if 'Response' in movie_data and movie_data['Response'] == 'False' and movie_data['Error'] == 'Movie not found!':
        return "Movie not found in the API."
    
    user = data_manager.get_user_by_id(user_id)
    # Extract relevant information from the API response
    director = movie_data.get('Director', '')
    year = movie_data.get('Year', '')
    rating = movie_data.get('imdbRating', '')
    url = movie_data["Poster"]
    if user:
        user_movies = user['movies']
        movie = data_manager.create_movie_obj(user_movies, movie_name,director,year,rating,url)
        if len(movie) > 0:
            user_movies.append(movie)
        else:
            return "Movie already exists in the list."
        data_manager.update_user_movies(user_id, user_movies)

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
    
    user_movies = user['movies']
    movie_found = False
    for movie in user_movies:
        if movie['id'] == movie_id:
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
    # Remove the user information from the session
    session.pop('user', None)
    return redirect('/login')

@app.errorhandler(404)
def page_not_found(e):
    """ Return an html page for the 404 error"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)