from sqlalchemy import func

from random import randint

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
        # print first_name, last_name, email, password, city, state, zipcode
        user = User(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    city=city,
                    state=state,
                    zipcode=zipcode)

        # print "USER", user
        #Add user to database
        db.session.add(user)

    db.session.commit()



def generate_reviews():

    print "Reviews"

    Review.query.delete()

    #query db to get all users
    users = User.query.all()

    #query db to get all studios
    studios = Studio.query.all()

    for user in users:
        for studio in studios:
            review = Review(user_id=user.user_id,
                            studio_id=studio.studio_id,
                            overall_rating=randint(4, 5),
                            amenities_rating=randint(1, 3),
                            cleanliness_rating=randint(4, 5),
                            class_size_rating=randint(4, 5),
                            schedule_rating=randint(1, 3),
                            pace_rating=randint(2, 3))
            db.session.add(review)

    db.session.commit()  



def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the maximum user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user id to be one more than the max id
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()

    generate_reviews()
