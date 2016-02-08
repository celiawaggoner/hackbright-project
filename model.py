"""Models and database functions for Hackbright project."""

from flask_sqlalchemy import SQLAlchemy

# Connect to the PostgreSQL database
db = SQLAlchemy()

##############################################################################
# Model definitions

class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

class Studio(db.Model):
    """Studio details"""

    __tablename__ = "studios"

    studio_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

class Review(db.Model):
    """User reviews of studios"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    studio_id = db.Column(db.Integer, db.ForeignKey("studios.studio_id"), nullable=False)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    # after /// is database name
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///project'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."