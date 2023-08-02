from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    profile_picture_url = db.Column(db.String(255), nullable=False)
    movies = db.relationship('Movies', backref='user', lazy=True)

    def to_dict(self, include_pass = True):
        """Convert the object attributes to a dictionary cause my app first was built for json."""
        """Convert the object attributes to a dictionary."""
        user_dict = {
            'id': self.id,
            'name': self.name,
            'profile_picture_url': self.profile_picture_url
        }

        if include_pass:
            user_dict['password'] = self.password

        return user_dict

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=False)  # Store year as a string
    rating = db.Column(db.String(3))  # Store rating as a string
    url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        """Convert the object attributes to a dictionary cause my app first was built for json."""
        return {
            'id': self.id,
            'name': self.name,
            'director': self.director,
            'year': self.year,
            'rating': self.rating,
            'url': self.url,
            'user_id': self.user_id
        }
    

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    def to_dict(self):
        """Convert the object attributes to a dictionary cause my app first was built for json."""
        return {
            'id': self.id,
            'review_text': self.review_text,
            'rating': self.rating,
            'user_id': self.user_id,
            'movie_id': self.movie_id
        }


# # creatd the tables 

# if __name__ == '__main__':
#     from app import app

#     # Initialize the SQLAlchemy extension with the Flask app
#     #  if i want to add more tables , need to comment the db.init_app in the app.py
#     db.init_app(app)

#     # Create the database tables
#     with app.app_context():
#         db.create_all()
