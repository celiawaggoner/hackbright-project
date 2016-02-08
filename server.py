from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db #data classes User, Review, Studio

# from collections import Counter

app = Flask(__name__)

#Need to establish secret key to use Flask sessions
app.secret_key = ""

#Raise an error if I use an undefined variable in Jinja
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show homepage."""

    return render_template("homepage.html")



if __name__ == "__main__":

    #Set to True when we call DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


