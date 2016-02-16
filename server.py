from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages, url_for, jsonify

from flask_debugtoolbar import DebugToolbarExtension

from flask_sqlalchemy import SQLAlchemy

from model import connect_to_db, db, User, Review, Studio, Favorite, Instructor, InstructorReview

import os

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

#create a client with API keys passed to Client constructor
auth = Oauth1Authenticator(
    consumer_key=os.environ['YELP_CONSUMER_KEY'],
    consumer_secret=os.environ['YELP_CONSUMER_SECRET'],
    token=os.environ['YELP_TOKEN'],
    token_secret=os.environ['YELP_TOKEN_SECRET']
)

client = Client(auth)

app = Flask(__name__)

#Need to establish secret key to use Flask sessions
app.secret_key = "mewmewmew"

#Raise an error if I use an undefined variable in Jinja
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show homepage."""

    return render_template("homepage.html")


@app.route('/register')
def registration_form():
    """Show user registration form"""

    return render_template("register.html")


@app.route('/registration-verification', methods=["POST"])
def check_if_new_user():
    """Check if user already exists. If not, add to database"""

    #assigned variables to email and password entered in registration form
    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")

    #getting a list of all users with that email that already exist in db
    users_with_email = db.session.query(User).filter(User.email == email).all()

    #checking to see if there are any existing users in db with that email
    #if not, add the new user info to db, add user to session, and redirect to profile
    #if already exists, flash and return to homepage
    if len(users_with_email) == 0:
        user = User(email=email, password=password, first_name=first_name,
                    last_name=last_name, city=city, state=state, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        user_id = user.user_id
        session['user'] = user_id
        flash("Congrats! You've successfully registered")
        return redirect('/user/' + str(user_id))
    else:
        flash("An account with this email address already exists. Please try again.")
        return redirect("/")


@app.route('/login')
def login_form():
    """Show login form"""

    return render_template("login.html")


@app.route('/login-verification', methods=["POST"])
def check_if_existing_user():
    """Check if user's email and password match. If so, log in."""

    #Get email and password form login form submission
    email = request.form.get("email")
    password = request.form.get("password")

    #assign user equal to the user in db with matching records
    user = db.session.query(User).filter((User.email == email) & (User.password == password)).first()

    #if user does not exist, flash message
    #if user does exist, add id to session and redirect to user profile
    if not user:
        flash("Information provided does not match our records. Please try again.")
        return redirect("/")
    else:
        user_id = user.user_id
        session['user'] = user_id
        flash("You have been successfully logged in.")
        return redirect('/user/' + str(user_id))


@app.route('/user/<user_id>')
def show_user_profile(user_id):
    """Show user profile"""

    #query db for user
    user = User.query.filter_by(user_id=user_id).one()

    #define attributes
    first_name = user.first_name
    last_name = user.last_name
    city = user.city
    state = user.state

    #query db for all of user's favorites
    favorites = user.favorites

    return render_template("user_profile.html", first_name=first_name,
                           last_name=last_name, city=city, state=state,
                           favorites=favorites)
                

@app.route('/logout')
def logout():
    """Logs out user"""

    session['user'] = None
    flash("You've successfully logged out!")
    return redirect('/')


@app.route('/studios')
def process_search():
    """Passes user imput into Yelp API search and return results"""

    #get input from search form
    zipcode = request.args.get('zipcode')

    #create a set of parameters
    params = {
        'term': 'Fitness & Instruction',
        'location': zipcode,
        'limit': 20
    }

    #query the Search API
    response = client.search(**params)

    #studios is a list of business dictionaries
    studios = response.businesses

    for studio in studios:
        studio_id = studio.id
        existing_studio = Studio.query.filter(Studio.studio_id == studio_id).all()
        if not existing_studio:
            studio = Studio(studio_id=studio_id, name=studio.name,
                        zipcode=studio.location.postal_code)
            db.session.add(studio)

    db.session.commit()

    return render_template("search_results.html", studios=studios)


@app.route('/studios/<studio_id>', methods=["GET"])
def show_studio_profile(studio_id):
    """Show studio profile and if a user is logged in,
        let them favorite the studio or add a review."""

    studio_id = studio_id
    studio = Studio.query.filter(Studio.studio_id == studio_id).one()
    name = studio.name
    zipcode = studio.zipcode

    user_id = session['user']

    params = {
        'term': name,
        'location': zipcode,
        'limit': 1
    }

    #query the Search API
    response = client.search(**params)

    #studios is list of studios in response
    studios = response.businesses

    favorited = Favorite.query.filter(Favorite.user_id == user_id, Favorite.studio_id == studio_id).first()

    return render_template("studio_profile.html", studios=studios,
                            name=name, zipcode=zipcode, favorited=favorited)


@app.route('/write-a-review/<studio_id>')
def show_review_form(studio_id):
    """Show blank review form"""

    id = studio_id

    return render_template("review.html", id=id)


@app.route('/review/studio', methods=["POST"])
def process_review_form():
    """Add input from review form to db and update overall scores"""

    overall_rating = request.form.get("overall_rating")
    amenities_rating = request.form.get("amenities_rating")
    cleanliness_rating = request.form.get("cleanliness_rating")
    class_size_rating = request.form.get("class_size_rating")
    schedule_rating = request.form.get("schedule_rating")
    pace_rating = request.form.get("pace_rating")
    studio_id = request.form.get("studio_id")

    #establish user id and studio id foreign keys
    user_id = session['user']

    #check if user already reviewed this studio
    #if already did, update ratings
    #if not, instansiate new review
    existing_review = Review.query.filter(Review.user_id == user_id, Review.studio_id == studio_id).one()
    if not existing_review:
        review = Review(user_id=user_id, studio_id=studio_id,
                        overall_rating=overall_rating,
                        cleanliness_rating=cleanliness_rating,
                        class_size_rating=class_size_rating,
                        schedule_rating=schedule_rating,
                        pace_rating=pace_rating)
        db.session.add(review)
        db.session.commit()

    #check if user already reviewed this instructor
    #if so, update rating
    #if not, instantiate instructor review
    instructor_review = InstructorReview()

    #check if instructor exists
    #if exists, update rating

    return redirect('/studios/' + str(studio_id))


@app.route('/check-if-favorite', methods=["GET"])
def check_favorite_status():
    """Checks if user has favorited studio"""

    #get studio info from ajax request
    studio_id = request.args.get("studio_id")

    #get user id from session
    user_id = session['user']

    #instantiate favorite and add/commit to db
    favorite = Favorite.query.filter(Favorite.user_id == user_id,
                                     Favorite.studio_id == studio_id).first()

    if favorite:
        return "true"
    else:
        return "false"


@app.route('/favorite/studio', methods=["POST"])
def favorite_studio():
    """Add favorite to database"""

    #get studio info from ajax request
    studio_id = request.form.get("studio_id")

    #get user id from session
    user_id = session['user']

    #instantiate favorite and add/commit to db
    favorite = Favorite.query.filter(Favorite.user_id == user_id, 
                                     Favorite.studio_id == studio_id).all()

    #add favorite to database if it doesn't already exist
    if not favorite:
        favorite = Favorite(user_id=user_id, studio_id=studio_id)
        db.session.add(favorite)
        db.session.commit()

        favorite_id = favorite.favorite_id
        session['favorite'] = favorite_id

    return jsonify({'favorite_studio': 'success'})

@app.route('/unfavorite/studio', methods=["POST"])
def unfavorite_studio():
    """Remove favorite from database"""

    studio_id = request.form.get("studio_id")

    user_id = session['user']

    favorite = Favorite.query.filter(Favorite.user_id == user_id, 
                                     Favorite.studio_id == studio_id).one()

    db.session.delete(favorite)
    db.session.commit()

    session['favorite'] = None

    return jsonify({'unfavorite_studio': 'success'})


if __name__ == "__main__":

    #Set to True when we call DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


