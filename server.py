from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Review, Studio, Favorite

import api

# from collections import Counter

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


