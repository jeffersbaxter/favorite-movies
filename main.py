import os

from flask import Flask, render_template, redirect, request, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

import moviedb

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


class SearchForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    submit = SubmitField('submit')


@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating.desc())).scalars().all()

    # update movie rankings to reflect current position
    for i in range(len(movies)):
        movies[i].ranking = i + 1

    return render_template("index.html", movies=movies)


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
    form = SearchForm()
    if request.method == "POST":
        query = form.title.data

        results = moviedb.search_movie(query)

        return render_template("select.html", results=results)
    return render_template("add.html", form=form)


@app.route('/select')
def select():
    movie_id = request.args.get('movie_id')
    if movie_id:
        details = moviedb.get_movie_details(movie_id)

        new_movie = Movie(
            title=details['title'],
            year=details['release_date'].split('-')[0],
            description=details['overview'],
            rating=1.0,
            ranking=len(db.session.query(Movie).all()) + 1,
            review="review does not exist",
            img_url=details['poster_path']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
