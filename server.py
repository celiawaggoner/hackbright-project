from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages, url_for, jsonify

from flask_debugtoolbar import DebugToolbarExtension

from flask_sqlalchemy import SQLAlchemy

from model import connect_to_db, db, User, Review, Studio, Favorite, Instructor, InstructorReview

import os

from sqlalchemy import func

import json

from fuzzywuzzy import fuzz, process

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

    #make key/value pairs for ratings and phrases
    preference_phrases = {"1": "Doesn't matter.",
                          "5": "Meh.",
                          "10": "Super important!"}

    amenities = preference_phrases.get(str(user.amenities_pref))
    cleanliness = preference_phrases.get(str(user.cleanliness_pref))
    class_size = preference_phrases.get(str(user.class_size_pref))
    schedule = preference_phrases.get(str(user.class_schedule_pref))
    pace = preference_phrases.get(str(user.class_pace_pref))

    return render_template("user_profile.html", first_name=first_name,
                           last_name=last_name, city=city, state=state,
                           favorites=favorites, reviews=reviews,
                           instructor_reviews=instructor_reviews,
                           user=user, amenities=amenities,
                           cleanliness=cleanliness, class_size=class_size,
                           schedule=schedule, pace=pace)


@app.route('/preferences.json')
def check_user_preferences():
    """Check for a user's existing preferences to prefill form"""

    user_id = session['user']

    user = User.query.filter(User.user_id == user_id).one()

    preferences = {"amenities_pref": user.amenities_pref,
                    "cleanliness_pref": user.cleanliness_pref,
                    "class_size_pref": user.class_size_pref,
                    "class_schedule_pref": user.class_schedule_pref,
                    "class_pace_pref": user.class_pace_pref}

    if user.amenities_pref > 0:
        return jsonify(preferences)


@app.route('/preferences', methods=["POST"])
def update_user_preferences():
    """Get user inputs from preferences form and update database"""

    #get user preferences from form
    amenities_pref = request.form.get("amenities")
    cleanliness_pref = request.form.get("cleanliness")
    class_size_pref = request.form.get("class_size")
    class_schedule_pref = request.form.get("class_schedule")
    class_pace_pref = request.form.get("class_pace")

    #query db for user
    user_id = session['user']
    user = User.query.filter(User.user_id == user_id).one()

    #add or update user preferences in db
    user.amenities_pref = amenities_pref
    user.cleanliness_pref = cleanliness_pref
    user.class_size_pref = class_size_pref
    user.class_schedule_pref = class_schedule_pref
    user.class_pace_pref = class_pace_pref

    db.session.commit()

    return redirect('/user/' + str(user_id))
             

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
    location = request.args.get('location')
    term = request.args.get('term')
    term = term.lower()

    #use fuzzy string comparison to check if search term somewhat matches
    #an option in the Yelp categories
    #if it does match, run the API request
    #if it doesn't match, but matches the name of a studio in the db, run API request
    #if not, redirect to homepage
    choices = ['barre classes', 'bootcamps', 'boxing', 'cardio classes',
               'dance studio', 'ems training', 'golf lessons', 'gyms',
               'martial arts', 'meditation centers', 'pilates', 'qigong',
               'swimming lessons', 'tai chi', 'trainers', 'yoga', 'climbing',
               'cycling', 'workout classes']

    category_result = process.extractOne(term, choices)

    #get names of studios already in database
    studios_in_db = Studio.query.filter(func.lower(Studio.name).like("%"+term[1:3]+"%")).all()
    studio_names = []
    for studio in studios_in_db:
        name = studio.name
        studio_names.append(name)

    name_result = process.extractOne(term, studio_names)

    if category_result[1] > 50:
        term = category_result[0]
            #create a set of parameters
        params = {
            'term': term,
            'location': location,
            'limit': 10,
            'sort': 0,
            'category_filter': 'fitness'
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

        lat = float(str(studios[0].location.coordinate.latitude))
        lng = float(str(studios[0].location.coordinate.longitude))

        return render_template("search_results.html", studios=studios,
                       lat=lat, lng=lng, location=location,
                       term=term)
    elif not name_result:
        flash("""Hmmm, we can't find any results that match your search.
               Please try again.""")
        return redirect("/")       
    elif name_result[1] > 90:
        term = name_result[0]
        params = {
            'term': term,
            'location': location,
            'limit': 10,
            'sort': 0,
            'category_filter': 'fitness'
        }

        #query the Search API
        response = client.search(**params)

        #studios is a list of business dictionaries
        studios = response.businesses

        lat = float(str(studios[0].location.coordinate.latitude))
        lng = float(str(studios[0].location.coordinate.longitude))

        return render_template("search_results.html", studios=studios,
                               lat=lat, lng=lng, location=location,
                               term=term)
    else:
        flash("""Hmmm, we can't find any results that match your search.
               Please try again.""")
        return redirect("/")


@app.route('/studios.json', methods=['GET'])
def get_studio_location():
    """Create a JSON object with studio latitudes and longitudes"""

    location = request.args.get("location")
    term = request.args.get("term")

    #create a set of parameters
    params = {
        'term': term,
        'location': location,
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

    #get user from db
    user = User.query.filter(User.user_id == user_id).one()

    params = {
        'term': name,
        'location': zipcode,
        'limit': 1
    }

    #query the Search API
    response = client.search(**params)

    #studios is list of studios in response
    studios = response.businesses

    #get lat and long for google map
    for studio in studios:
        latitude = float(str(studio.location.coordinate.latitude))
        longitude = float(str(studio.location.coordinate.longitude))

    favorited = Favorite.query.filter(Favorite.user_id == user_id, Favorite.studio_id == studio_id).first()

    #get studio from db
    studio_db = Studio.query.filter(Studio.studio_id == studio_id).first()

    
    reviews = studio_db.reviews

    #get all tip_texts from reviews with tips included
    tips = []
    for review in reviews:
        if review.tip_text is not None:
            tip = review.tip_text
            tips.append(tip)

    #get review count from length of reviews list
    review_count = len(reviews)

    #create key value pairs for star ratings
    stars = {"0": [],
             "1": ['*'],
             "2": ['*', '*'],
             "3": ['*', '*', '*'],
             "4": ['*', '*', '*', '*'],
             "5": ['*', '*', '*', '*', '*']}

    empties = {"5": [],
               "4": ['*'],
               "3": ['*', '*'],
               "2": ['*', '*', '*'],
               "1": ['*', '*', '*', '*'],
               "0": []}

    #use weighted average to create user-specific score for this studio
    if review_count > 0:
        if user.amenities_pref:
            individual_score = ((int(user.amenities_pref) * int(studio_db.amenities_rating))
                            + (int(user.cleanliness_pref) * int(studio_db.cleanliness_rating))
                            + (int(user.class_size_pref) * int(studio_db.class_size_rating))
                            + (int(user.class_schedule_pref) * int(studio_db.schedule_rating))
                            + (int(user.class_pace_pref) * int(studio_db.pace_rating))) / (int(user.amenities_pref)
                            + int(user.cleanliness_pref)
                            + int(user.class_size_pref) + int(user.class_schedule_pref)
                            + int(user.class_pace_pref))
    else:
        individual_score = "Set your preferences to get an individualized score for each studio!"

        #translate scores in star ratings
        individual_stars = stars.get(str(individual_score))
        individual_empties = empties.get(str(individual_score))

    amenities_stars = stars.get(str(studio_db.amenities_rating))
    cleanliness_stars = stars.get(str(studio_db.cleanliness_rating))
    class_size_stars = stars.get(str(studio_db.class_size_rating))
    schedule_stars = stars.get(str(studio_db.schedule_rating))

    amenities_empties = empties.get(str(studio_db.amenities_rating))
    cleanliness_empties = empties.get(str(studio_db.cleanliness_rating))
    class_size_empties = empties.get(str(studio_db.class_size_rating))
    schedule_empties = empties.get(str(studio_db.schedule_rating))

    #get list of instructors 
    instructors = studio_db.instructors

    instructor_details = {}
    
    # get instructor average rating, get the top rated instructor
    # translate score into star rating
    for instructor in instructors:
        instructor_details[str(instructor.name)] = []
        for review in instructor.instructorreviews:
            instructor_details[str(instructor.name)].append(review.rating)
            average = sum(instructor_details[str(instructor.name)]) / len(instructor_details[str(instructor.name)])
        instructor_details[str(instructor.name)] = average
        instructor_stars = stars.get(str(average))
        instructor_empties = empties.get(str(average))

    if len(instructor_details) > 0:
        top_instructor = max(instructor_details, key=instructor_details.get)
        instructor_stars = stars.get(str(instructor_details[top_instructor]))
        instructor_empties = empties.get(str(instructor_details[top_instructor]))
    else:
        top_instructor = "Review this studio to rate your instructor!"
        instructor_stars = stars.get("0")
        instructor_empties = empties.get("0")

    #create key value pairs to rating and phrase
    pace = {"1": "Didn't break a sweat.",
            "2": "Pretty good workout.",
            "3": "I was dying!"}

    pace_rating = pace.get(str(studio_db.pace_rating))

    return render_template("studio_profile.html", studios=studios,
                           name=name, zipcode=zipcode, favorited=favorited,
                           id=id, studio_db=studio_db, reviews=reviews,
                           instructors=instructors,
                           review_count=review_count,
                           latitude=latitude, longitude=longitude,
                           pace_rating=pace_rating, individual_stars=individual_stars,
                           tips=tips, instructor_details=instructor_details,
                           amenities_stars=amenities_stars,
                           cleanliness_stars=cleanliness_stars,
                           class_size_stars=class_size_stars,
                           schedule_stars=schedule_stars,
                           amenities_empties=amenities_empties,
                           cleanliness_empties=cleanliness_empties,
                           class_size_empties=class_size_empties,
                           schedule_empties=schedule_empties,
                           individual_empties=individual_empties,
                           instructor_stars=instructor_stars,
                           instructor_empties=instructor_empties,
                           top_instructor=top_instructor)


@app.route('/instructor-move-form', methods=["POST"])
def check_instructor_move():
    """Update db with instructor move info"""

    #get user input from form
    name = request.form.get("name")
    old_studio_id = request.form.get("studio_id")
    studio = request.form.get("studio")
    zipcode = request.form.get("zipcode")

    #check if user inputed studio exists in db
    studio_in_db = Studio.query.filter(Studio.name == studio, Studio.zipcode == zipcode).first()

    #query db for instructor record
    instructor = Instructor.query.filter(Instructor.name == name, Instructor.studio_id == old_studio_id).first()

    #if exists, find instructor in db and update studio id
    if studio_in_db:
        instructor.studio_id = studio_in_db.studio_id
        db.session.commit()
     #if does not exist, alert user
    else:
        flash("""Sorry! We couldn't find that studio. Please search for it
                and add a review for this instructor.""")

    return redirect('/studios/' + str(old_studio_id))



@app.route('/write-a-review/<studio_id>')
def show_review_form(studio_id):
    """Show blank review form"""

    id = studio_id

    return render_template("review.html", id=id)


@app.route('/review/studio', methods=["POST"])
def process_review_form():
    """Add input from review form to db and update overall scores"""

    tip_text = request.form.get("tip_text")
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
                        tip_text=tip_text,
                        amenities_rating=amenities_rating,
                        cleanliness_rating=cleanliness_rating,
                        class_size_rating=class_size_rating,
                        schedule_rating=schedule_rating,
                        pace_rating=pace_rating,
                        favorite_class=favorite_class)
        db.session.add(review)
        db.session.commit()
    if existing_review:
        existing_review.tip_text = tip_text
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

    studio = Studio.query.filter(Studio.studio_id == studio_id).first()

    all_reviews = studio.reviews

    #get number of reviews to use for average
    max_id = len(all_reviews)

    amenities_total = 0
    cleanliness_total = 0
    class_size_total = 0
    class_schedule_total = 0
    class_pace_total = 0

    for review in all_reviews:
        amenities_total += int(review.amenities_rating)
        cleanliness_total += int(review.cleanliness_rating)
        class_size_total += int(review.class_size_rating)
        class_schedule_total += int(review.schedule_rating)
        class_pace_total += int(review.pace_rating)


    #if this studio has already been reviewed, calculate the average
    #if not, add this first review to studio db

    if len(all_reviews) > 1:
        # studio.overall_rating = (overall_total + (int(overall_rating))) / int(max_id)
        studio.amenities_rating = (amenities_total+ (int(amenities_rating))) / int(max_id)
        studio.cleanliness_rating = (cleanliness_total + (int(cleanliness_rating))) / int(max_id)
        studio.class_size_rating = (class_size_total + (int(class_size_rating))) / int(max_id)
        studio.schedule_rating = (class_schedule_total + (int(schedule_rating))) / int(max_id)
        studio.pace_rating = (class_pace_total + (int(pace_rating))) / int(max_id)
        db.session.commit()
    else:
        # studio.overall_rating = overall_rating
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
    # DebugToolbarExtension(app)

    app.run()


