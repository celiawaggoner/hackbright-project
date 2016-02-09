from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Review, Studio, Favorite, Instructor, InstructorReview

import requests

import os

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

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

    # url_params = {
    #     'term': 'Fitness & Instruction'.replace(' ', '+'),
    #     'location': zipcode.replace(' ', '+'),
    #     'limit': 10
    # }

    # r = requests.get('api.yelp.com', '/v2/search/', params=url_params)

    # consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    # oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    # token = oauth2.Token(TOKEN, TOKEN_SECRET)
    # oauth_request.sign_request(
    # oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    # signed_url = oauth_request.to_url()

    # payload = {'oauth_consumer_key': CONSUMER_KEY, 'oauth_token': TOKEN,
    #             'oauth_signature_method': hmac-sha1,
    #             'oauth_signature': signed_url,
    #             'oauth_timestamp': oauth2.generate_timestamp(),
    #             'oauth_nonce': oauth2.generate_nonce(),
    #             'term': 'Fitness & Instruction',
    #             'location': zipcode,
    #             'limit': 10}

    # r = requests.get('https://api.yelp.com/v2/search', params=payload)

    # # print(r.url)

    # studios_dict = r.json()

    # return studios_dict

    # return render_template

    params = {
        'term': 'Fitness & Instruction',
        'location': zipcode,
        'limit': 10
    }

    response = client.search(**params)

    names = []

    for business in response.businesses:
        name = business.name
        names.append(name)

    return render_template("search_results.html", names=names)


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


