from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages

from flask_debugtoolbar import DebugToolbarExtension

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
    # email = request.form.get("email")
    # password = request.form.get("password")

    #getting a list of all users with that email that already exist in db
    # users_with_email = db.session.query(User).filter(User.email == email).all()

    #checking to see if there are any existing users in db with that email
    #if not, add the new user info to db, add user to session, and redirect to profile
    #if already exists, flash and return to homepage
    # if len(users_with_email) == 0:
    #     user = User(email=email, password=password)
    #     user_id = user.user_id
    #     db.session.add(user)
    #     db.session.commit()
    #     session['user'] = user_id
    #     flash("Congrats! You've successfully registered")
    #     return redirect('/user/' + str(user_id))
    # else:
    #     flash("This email address has already been registered. Please try again.")
    #     return redirect("/")


@app.route('/login')
def login_form():
    """Show login form"""

    return render_template("login.html")


@app.route('/login-verification', methods=["POST"])
def check_if_existing_user():
    """Check if user's email and password match. If so, log in."""


@app.route('/user/<int:user_id>')
def show_user_profile(user_id):
    """Show user profile"""

    return render_template("user_profile.html")


@app.route('/logout')
def logout():
    """Logs out user"""

    # session['user'] = None
    # flash("Logged out!")
    # return redirect('/')


@app.route('/search-results')
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

    return render_template("search_results.html", studios=studios)


@app.route('/studio/<int:studio_id>')
def show_studio_profile(studio_id):
    """Show studio profile"""

    return render_template("studio_profile.html")


@app.route('/write-a-review')
def show_review_form():
    """Show blank review form"""

    return render_template("review.html")



if __name__ == "__main__":

    #Set to True when we call DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


