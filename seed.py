from sqlalchemy import func

from model import User
from model import Studio
from model import Review
from model import Instructor
from model import InstructorReview
from model import Favorite

from model import connect_to_db, db
from server import app


def load_users():
    """Add users into database"""

        #Add user to database
        db.session.add(user)

    db.session.commit()
