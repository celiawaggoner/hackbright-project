"""Models and database functions for Hackbright project."""

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import func

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
    amenities_pref = db.Column(db.Integer, nullable=True)
    cleanliness_pref = db.Column(db.Integer, nullable=True)
    class_size_pref = db.Column(db.Integer, nullable=True)
    class_schedule_pref = db.Column(db.Integer, nullable=True)
    class_pace_pref = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Studio(db.Model):
    """Studio details"""

    __tablename__ = "studios"

    studio_id = db.Column(db.String(150), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(25), nullable=False)
    top_instructor = db.Column(db.String(50), nullable=True)
    top_class = db.Column(db.String(50), nullable=True)
    amenities_rating = db.Column(db.Integer, nullable=True)
    cleanliness_rating = db.Column(db.Integer, nullable=True)
    class_size_rating = db.Column(db.Integer, nullable=True)
    schedule_rating = db.Column(db.Integer, nullable=True)
    pace_rating = db.Column(db.String(25), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Studio studio_id=%s name=%s>" % (self.studio_id, self.name)

    #Define relationship to instructors 
    instructors = db.relationship("Instructor", backref="studio")


class Review(db.Model):
    """User reviews of studios"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    studio_id = db.Column(db.String(150), db.ForeignKey("studios.studio_id"), nullable=False)
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
    studio_id = db.Column(db.String(150), db.ForeignKey("studios.studio_id"), nullable=False)
    notes = db.Column(db.String(500), nullable=True)

    #Define relationship to user
    user = db.relationship("User", backref="favorites")

    #Define relationship to studio
    studio = db.relationship("Studio", backref="favorites")


class Instructor(db.Model):
    """Instructors"""

    __tablename__ = "instructors"

    instructor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    studio_id = db.Column(db.String(150), db.ForeignKey("studios.studio_id"), nullable=False)
    name = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Instructor instructor_id=%s name=%s>" % (self.instructor_id, self.name)


class InstructorReview(db.Model):
    """User reviews of instructors"""

    __tablename__ = "instructorreviews"

    instructor_review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructors.instructor_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    rating = db.Column(db.Integer, nullable=True)

    #Define relationship to user
    user = db.relationship("User", backref="instructorreviews")

    #Define relationship to instructor 
    instructor = db.relationship("Instructor", backref="instructorreviews")

#############################################################################
# Add example data for testing


def example_data_users():
    """Create sample user data"""

    #Empty out existing data
    User.query.delete()

    celia = User(user_id=2, first_name='Celia', last_name='Waggoner',
                 email="celia@test.com", password="123", city="San Francisco",
                 state="CA", zipcode='94110',
                 amenities_pref=1, cleanliness_pref=5, class_size_pref=10,
                 class_schedule_pref=5, class_pace_pref=1)
    pam = User(user_id=3, first_name='Pam', last_name='Geick',
               email="pam@test.com", password="456", city="Rocky River",
               state="OH", zipcode='44116',
               amenities_pref=1, cleanliness_pref=1, class_size_pref=1,
               class_schedule_pref=1, class_pace_pref=1)
    amber = User(user_id=4, first_name='Amber', last_name='Lynn',
                 email="amber@fake.com", password="789", city="Brooklyn",
                 state="NY", zipcode='11201',
                 amenities_pref=10, cleanliness_pref=10, class_size_pref=10,
                 class_schedule_pref=10, class_pace_pref=10)

    db.session.add_all([celia, pam, amber])
    db.session.commit()


##############################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///project'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    # after /// is database name
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
  
