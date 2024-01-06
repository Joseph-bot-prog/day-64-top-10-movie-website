from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_API_KEY = "5c35af1a990a2fae99c055c2957a2541"  # <- Remove mine and add yours using www.movie.db.com
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

# Create the table in the database within the application context
with app.app_context():
    db.create_all()

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i, movie in enumerate(all_movies):
        movie.ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        print(f"Movie title: {movie_title}")  # Debugging statement
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json().get("results", [])
        print(f"API Response: {data}")  # Debugging statement
        return render_template("select.html", options=data, form=form)
    return render_template("add.html", form=form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    print(f"Movie API ID: {movie_api_id}")  # Debugging statement
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        print(f"Movie API Response: {data}")  # Debugging statement
        new_movie = Movie(
            title=data.get("title"),
            year=int(data.get("release_date", "").split("-")[0]),
            img_url=f"{MOVIE_DB_IMAGE_URL}{data.get('poster_path', '')}",
            description=data.get("overview")
        )
        print(f"New Movie Object: {new_movie.__dict__}")  # Debugging statement
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie", id=new_movie.id))

# Rest of your routes remain unchanged
# ...

if __name__ == '__main__':
    app.run(debug=True)
