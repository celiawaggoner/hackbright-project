from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages, url_for, jsonify

from flask_debugtoolbar import DebugToolbarExtension

from flask_sqlalchemy import SQLAlchemy

from model import connect_to_db, db, User, Review, Studio, Favorite, Instructor, InstructorReview

import os

from sqlalchemy import func

import json

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

    reviews = user.reviews

    instructor_reviews = user.instructorreviews

    return render_template("user_profile.html", first_name=first_name,
                           last_name=last_name, city=city, state=state,
                           favorites=favorites, reviews=reviews,
                           instructor_reviews=instructor_reviews)
              

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
        'limit': 10
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

    #create a dictionary with studio name and lats and longs
    #pass dictionary to javascript to iterate over and create
    #multiple markers

    # import pdb
    # pdb.set_trace()

    lat = float(str(studios[0].location.coordinate.latitude))
    lng = float(str(studios[0].location.coordinate.longitude))


    return render_template("search_results.html", studios=studios,
                           lat=lat, lng=lng, zipcode=zipcode)

@app.route('/studios.json', methods=['GET'])
def get_studio_location():
    """Create a JSON object with latitudes and longitudes"""

    zipcode = request.args.get("zipcode")

    #create a set of parameters
    params = {
        'term': 'Fitness & Instruction',
        'location': zipcode,
        'limit': 10
    }

    #query the Search API
    response = client.search(**params)

    #studios is a list of business dictionaries
    studios = response.businesses

    results = {}
    for studio in studios:
        results[str(studio.name)] = {"latitude": float(str(studio.location.coordinate.latitude)),
                                     "longitude": float(str(studio.location.coordinate.longitude))}

    # import pdb
    # pdb.set_trace()


    return jsonify(results)


@app.route('/studios/<studio_id>', methods=["GET"])
def show_studio_profile(studio_id):
    """Show studio profile and if a user is logged in,
        let them favorite the studio or add a review."""

    id = studio_id
    studio = Studio.query.filter(Studio.studio_id == studio_id).first()
    name = str(studio.name)
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

    # import pdb
    # pdb.set_trace()

    #get lat and long for google map
    for studio in studios:
        latitude = float(str(studio.location.coordinate.latitude))
        longitude = float(str(studio.location.coordinate.longitude))

    favorited = Favorite.query.filter(Favorite.user_id == user_id, Favorite.studio_id == studio_id).first()

    #get studio from db
    studio_db = Studio.query.filter(Studio.studio_id == studio_id).one()

    reviews = studio_db.reviews

    review_count = len(reviews)

    instructors = studio_db.instructors      

    return render_template("studio_profile.html", studios=studios,
                           name=name, zipcode=zipcode, favorited=favorited,
                           id=id, studio_db=studio_db, reviews=reviews,
                           instructors=instructors,
                           review_count=review_count,
                           latitude=latitude, longitude=longitude)


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

    name = request.form.get("name")
    rating = request.form.get("instructor_rating")

    favorite_class = request.form.get("fav_class")

    studio_id = request.form.get("studio_id")


    #establish user id and studio id foreign keys
    user_id = session['user']

    #check if user already reviewed this studio
    #if already did, update ratings
    #if not, instansiate new review
    existing_review = Review.query.filter(Review.user_id == user_id, Review.studio_id == studio_id).first()

    if not existing_review:
        review = Review(user_id=user_id, studio_id=studio_id,
                        overall_rating=overall_rating,
                        amenities_rating=amenities_rating,
                        cleanliness_rating=cleanliness_rating,
                        class_size_rating=class_size_rating,
                        schedule_rating=schedule_rating,
                        pace_rating=pace_rating,
                        favorite_class=favorite_class)
        db.session.add(review)
        db.session.commit()
    if existing_review:
        existing_review.overall_rating = overall_rating
        existing_review.cleanliness_rating = cleanliness_rating
        existing_review.class_size_rating = class_size_rating
        existing_review.schedule_rating = schedule_rating
        existing_review.pace_rating = pace_rating
        existing_review.favorite_class = favorite_class
        db.session.commit()

    #check if this instructor exists in the database
    #if so, use id for review
    #if not, add to database
    instructor = Instructor.query.filter(Instructor.name == name,
    Instructor.studio_id == studio_id).first()

    if not instructor:
        instructor = Instructor(studio_id=studio_id, name=name)
        db.session.add(instructor)
        db.session.commit()

    instructor_id = instructor.instructor_id

    #check if user already reviewed this instructor
    #if so, update rating
    #if not, instantiate instructor review

    existing_instructor_review = InstructorReview.query.filter(InstructorReview.user_id == user_id, InstructorReview.instructor_id == instructor_id).first()

    if not existing_instructor_review:
        instructorreview = InstructorReview(instructor_id=instructor_id,
                                            user_id=user_id,
                                            rating=rating)
        db.session.add(instructorreview)
        db.session.commit()
    if existing_instructor_review:
        existing_instructor_review.rating = rating
        db.session.commit()

    #update studios overall scores in db with this user's scores

    #get highest review_id to use as number of reviews for average
    
    # import pdb
    # pdb.set_trace()

    max = db.session.query(func.max(Review.review_id)).one()
    for item in max:
        max_id = item

    studio = Studio.query.filter(Studio.studio_id == studio_id).first()
    #get studio ratings that are currently in db
    old_overall_rating = studio.overall_rating
    old_amenities_rating = studio.amenities_rating
    old_cleanliness_rating = studio.cleanliness_rating
    old_class_size_rating = studio.class_size_rating
    old_schedule_rating = studio.schedule_rating
    old_pace_rating = studio.pace_rating

    all_reviews = studio.reviews


    #if this studio has already been reviewed, calculate the average
    #if not, add this first review to studio db
    # if len(all_reviews) > 1:
    #     studio.overall_rating = ((float(str(old_overall_rating))) + (float(str(overall_rating)))) / float(str(max_id))
    #     studio.amenities_rating = ((float(str(old_amenities_rating))) + (float(str(amenities_rating)))) / float(str(max_id))
    #     studio.cleanliness_rating = ((float(str(old_cleanliness_rating))) + (float(str(cleanliness_rating)))) / float(str(max_id))
    #     studio.class_size_rating = ((float(str(old_class_size_rating))) + (float(str(class_size_rating)))) / float(str(max_id))
    #     studio.schedule_rating = ((float(str(old_schedule_rating))) + (float(str(schedule_rating)))) / float(str(max_id))
    #     studio.pace_rating = ((float(str(old_pace_rating))) + (float(str(pace_rating)))) / float(str(max_id))
    #     db.session.commit()
    if len(all_reviews) > 1:
        studio.overall_rating = (old_overall_rating + (float(str(overall_rating)))) / float(str(max_id))
        studio.amenities_rating = (old_amenities_rating + (float(str(amenities_rating)))) / float(str(max_id))
        studio.cleanliness_rating = (old_cleanliness_rating + (float(str(cleanliness_rating)))) / float(str(max_id))
        studio.class_size_rating = (old_class_size_rating + (float(str(class_size_rating)))) / float(str(max_id))
        studio.schedule_rating = (old_schedule_rating + (float(str(schedule_rating)))) / float(str(max_id))
        studio.pace_rating = (old_pace_rating + (float(str(pace_rating)))) / float(str(max_id))
        db.session.commit()
    else:
        studio.overall_rating = overall_rating
        studio.amenities_rating = amenities_rating
        studio.cleanliness_rating = cleanliness_rating
        studio.class_size_rating = class_size_rating
        studio.schedule_rating = schedule_rating
        studio.pace_rating = pace_rating
        db.session.commit()

    return redirect('/studios/' + str(studio_id))


@app.route('/check-if-favorite', methods=["GET"])
def check_favorite_status():
    """Checks if user has favorited studio"""

    # import pdb
    # pdb.set_trace()

    #get studio info from ajax request
    studio_id = request.args.get("studio_id")

    studio_id = str(studio_id)

    #get user id from session
    user_id = session['user']

    #instantiate favorite and add/commit to db
    favorite = Favorite.query.filter(Favorite.user_id == user_id,
                                     Favorite.studio_id == studio_id).first()

    if not favorite:
        return "false"
    else:
        return "true"


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


