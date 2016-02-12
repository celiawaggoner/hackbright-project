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
    city = db.Column(db.String(25), nullable=False)
    state = db.Column(db.String(25), nullable=False)
    zipcode = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Studio(db.Model):
    """Studio details"""

    __tablename__ = "studios"

    studio_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    zipcode = db.Column(db.String(25), nullable=False)
    website_url = db.Column(db.String(100), nullable=True)
    class_type = db.Column(db.String(150), nullable=True)
    top_instructor = db.Column(db.String(50), nullable=True)
    top_class = db.Column(db.String(50), nullable=True)
    yelp_rating_url = db.Column(db.String(100), nullable=True)
    yelp_image_url = db.Column(db.String(100), nullable=True)
    overall_rating = db.Column(db.Integer, nullable=True)
    amenities_rating = db.Column(db.Integer, nullable=True)
    cleanliness_rating = db.Column(db.Integer, nullable=True)
    class_size_rating = db.Column(db.Integer, nullable=True)
    schedule_rating = db.Column(db.Integer, nullable=True)
    pace_rating = db.Column(db.String(25), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Studio studio_id=%s name=%s>" % (self.studio_id, self.name)


class Review(db.Model):
    """User reviews of studios"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    studio_id = db.Column(db.Integer, db.ForeignKey("studios.studio_id"), nullable=False)
    overall_rating = db.Column(db.Integer, nullable=True)
    amenities_rating = db.Column(db.Integer, nullable=True)
    cleanliness_rating = db.Column(db.Integer, nullable=True)
    class_size_rating = db.Column(db.Integer, nullable=True)
    schedule_rating = db.Column(db.Integer, nullable=True)
    pace_rating = db.Column(db.String(25), nullable=True)
    favorite_instructor = db.Column(db.String(25), nullable=True)
    favorite_class = db.Column(db.String(25), nullable=True)
    tip_text = db.Column(db.String(250), nullable=True)

    #Define relationship to user
    user = db.relationship("User", backref="reviews")

    #Define relationship to studio
    studio = db.relationship("Studio", backref="reviews")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Review review_id=%s user_id=%s studio_id=%s>" % (self.review_id, self.user_id, self.studio_id)


class Favorite(db.Model):
    """User's favorited studios"""

    __tablename__ = "favorites"

    favorite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    studio_id = db.Column(db.Integer, db.ForeignKey("studios.studio_id"), nullable=False)
    notes = db.Column(db.String(500), nullable=True)

    #Define relationship to user
    user = db.relationship("User", backref="favorites")


class Instructor(db.Model):
    """Instructors"""

    __tablename__ = "instructors"

    instructor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    studio_id = db.Column(db.Integer, db.ForeignKey("studios.studio_id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    #Define relationship to studio
    studio = db.relationship("Studio", backref="studios")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Instructor instructor_id=%s name=%s>" % (self.instructor_id, self.name)


class InstructorReview(db.Model):
    """User reviews of instructors"""

    __tablename__ = "instructor-reviews"

    instructor_review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructors.instructor_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    #Define relationship to user
    user = db.relationship("User", backref="instructor-reviews")


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
