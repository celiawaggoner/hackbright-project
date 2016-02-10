from sqlalchemy import func

from model import User
from model import Studio
from model import Review
from model import Instructor
from model import InstructorReview
from model import Favorite

from model import connect_to_db, db
from server import app

# from faker import Faker
# fake = Faker()
# fake.seed(4321)


def load_users():
    """Add users into database"""

    print "Users"

    # Delete all rows in existing table to avoid duplicating data
    User.query.delete()

    # Read user file and insert data
    for row in open("seed_data/users.txt"):
        row = row.rstrip()
        
        first_name, last_name, email, password, city, state, zipcode = row.split(",")

        print first_name, last_name, email, password, city, state, zipcode 
        user = User(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    city=city,
                    state=state,
                    zipcode=zipcode)
        print "USER", user
        #Add user to database
        db.session.add(user)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
