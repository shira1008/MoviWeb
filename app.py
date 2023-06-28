from flask import Flask, render_template, request, redirect, url_for, abort
from datamanager.json_data_manager import JSONDataManager
from fetching_from_api import fetch_data

app = Flask(__name__)
data_manager = JSONDataManager('data.json')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def favorite_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    user = data_manager.get_user_by_id(user_id)
    if not user:
        abort(404, "User not found.")
    user_name = user["name"]
    return render_template('user_movies.html', movies=movies, user_id=user_id,  user_name= user_name )


@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if request.method == "POST":
        name = request.form.get('name')

        data_manager.add_new_user(name)

        return redirect(url_for('list_users'))
        
    return render_template('add_user.html')


@app.route('/add_movie/<int:user_id>', methods=['POST'])
def add_movie(user_id):
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
        for movie in user_movies:
            if movie['name'] == movie_name:
                return "Movie already exists in the list."
        
        new_movie_id = data_manager.generate_movie_id(user_movies)
        movie = {
            'id': new_movie_id,
            'name': movie_name.capitalize(),
            'director': director,
            'year': year,
            'rating':rating,
            'url': url
        }
        user_movies.append(movie)
        data_manager.update_user_movies(user_id, user_movies)
        return redirect(url_for('favorite_movies', user_id=user_id))
    else:
        return "User not found."
    

@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    #check the user
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found."
    
    # Retrieve the user's movies
    # user_movies = user['movies']
    user_movies = data_manager.get_user_movies(user_id)
    movie = None
    for one_movie in user_movies:
        if one_movie['id'] == movie_id:
            movie = one_movie
    
    if not movie:
        abort(404, "Movie not found.")
            
    
    if request.method == "POST":
        movie_name = request.form.get('movie_name')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')
        if float(rating) > 10 or float(rating) < 0 : 
            return "Please enter a value between 0-10"

        for a_movie in user_movies:
            if a_movie['id'] == movie_id:
                    a_movie['name'] = movie_name
                    a_movie['director'] = director
                    a_movie['year'] = year
                    a_movie['rating'] = rating

        data_manager.update_user_movies(user_id, user_movies)
        return redirect(url_for('favorite_movies', user_id=user_id))

    return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie=movie)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
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

   

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)