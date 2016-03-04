from model import User, Studio, Review, Favorite, Instructor, InstructorReview, example_data_users, connect_to_db, db
from server import app
import server
from unittest import TestCase
import doctest
from flask import Flask, session

class FlaskTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data_users()


        # initiate a session
        with self.client.session_transaction() as session:
            session['user'] = '2'
            self.client.set_cookie('localhost', 'MYCOOKIE', 'cookie_value')

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

#############################################################################
# Test functions that query the database.

    def test_process_signup_new_user(self):
        """Test signup form to process new user."""

        result = self.client.post('/registration-verification',
                                  data={'firstname': "Dave",
                                        'lastname': "White",
                                        'email': "dave@dave.com",
                                        'password': 'password123',
                                        'city': "San Francisco",
                                        'state': "CA",
                                        'zipcode': "94105",},
                                  follow_redirects=True)
        self.assertEqual(result.status_code, 200)

    def test_process_signup_exisiting_user(self):
        """Test signup form to process an existing user."""

        result = self.client.post('/process-signup',
                                  data={'firstname': "Celia",
                                        'lastname': "Waggoner",
                                        'zipcode': "94110",
                                        'email': "celia@test.com",
                                        'password': '123',
                                        'city': "San Francisco",
                                        'state': "CA"},
                                  follow_redirects=True)
        self.assertIn('/', result.data)


    def test_process_correct_login(self):
        """Test login form to process existing user"""

        result = self.client.post("/login-verification",
                                  data={"email": 'celia@test.com', 'password': '123'},
                                  follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been successfully logged in.", result.data)


    def test_process_incorrect_login(self):
        """Test login form to process unknown user."""

        result = self.client.post("/process-login",
                                  data={"email": 'fake@test.com', 'password': 'fake'},
                                  follow_redirects=True)

        self.assertIn('/', result.data)

    def test_logout(self):
        """Test logout"""

        result = self.client.get('/logout', follow_redirects=True)

        self.assertIn('/', result.data)


#############################################################################
# Test functions that render a template.

    def test_load_homepage(self):
        """Test to confirm the homepage loads correctly"""

        result = self.client.get('/')

        self.assertEqual(result.status_code, 200)

    def test_load_login(self):
        """Test to confirm the login page loads correctly"""

        result = self.client.get('/login')

        self.assertEqual(result.status_code, 200)

    def test_load_register(self):
        """Test to confirm the registration page loads correctly"""

        result = self.client.get('/register')

        self.assertEqual(result.status_code, 200)

    def test_load_logout(self):
        """Tests to confirm the logout page loads correctly."""

        result = self.client.get('/logout')

        self.assertEqual(result.status_code, 302)
        self.assertIn('/', result.data)


#############################################################################
# Test functions to see if they're an instance of a built-in class

    def test_preferences_json(self):
        """Test to see if /preferences.json route will return json object."""

        response = self.client.get("/preferences.json")

        self.assertIsInstance(response, object)

    def test_studios_json(self):
        """Test to see if /studios.json route will return json object."""

        response = self.client.get("/studios.json")

        self.assertIsInstance(response, object)

    def test_favorite_json(self):
        """Test to see if /favorite/studio route will return json object."""

        response = self.client.get("/favorite/studio")

        self.assertIsInstance(response, object)

    def test_unfavorite_json(self):
        """Test to see if /unfavorite/studio route will return json object."""

        response = self.client.get("/unfavorite/studio")

        self.assertIsInstance(response, object)



#############################################################################

if __name__ == "__main__":
    import unittest

    unittest.main()
