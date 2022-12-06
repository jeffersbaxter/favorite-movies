import os

from flask import Flask, render_template, redirect, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
db = SQLAlchemy(app)
Bootstrap(app)

with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Float, nullable=False)
        ranking = db.Column(db.Integer, nullable=False)
        review = db.Column(db.String(250), nullable=False)
        img_url = db.Column(db.String(250), nullable=False)

        def __repr__(self):
            return f'<Book {self.title}'


class MovieEditForm(FlaskForm):
    id = HiddenField('id')
    rating = StringField('rating')
    review = StringField('review')
    submit = SubmitField('Submit')


class AddMovieForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    year = StringField('year')
    description = StringField('description')
    rating = StringField('rating')
    ranking = StringField('ranking')
    review = StringField('review')
    img_url = StringField('image url')
    submit = SubmitField('submit')


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = MovieEditForm()
    if request.method == "GET":
        movie_id = request.args.get("id")
        selected = Movie.query.get(movie_id)
        form.id.data = movie_id
        form.rating.data = selected.rating
        form.review.data = selected.review
        return render_template("edit.html", movie=selected, form=form)
    if form.validate_on_submit():
        movie_id = form.id.data
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect("/")


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')

    # DELETE RECORD
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect("/")


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if request.method == "POST":
        new_movie = Movie(
            title=form.title.data,
            year=int(form.year.data),
            description=form.description.data,
            rating=float(form.rating.data),
            ranking=int(form.ranking.data),
            review=form.review.data,
            img_url=form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect("/")
    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
