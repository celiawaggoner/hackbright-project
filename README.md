![Pulse Logo](/static/img/design.png)

Learn more about the developer: www.linkedin.com/in/celiawaggoner

Pulse is a web app created by Celia Waggoner that helps people find workout studios. Users can also create an account to review studios and instructors, save their favorite studios, and set weighted preferences in order to view an individualized score for each studio. 

## Table of Contents
* [Technologies Used](#technologiesused)
* [Features](#features)
* [Version 2.0](#v2)
* [Author](#author)

## <a name="technologiesused"></a>Technologies Used

* Python
* Flask
* PostgreSQL
* SQLAlchemy
* Javascript/jQuery
* AJAX/JSON
* HTML/CSS
* Jinja2
* Bootstrap
* Yelp API
* Google Maps API

(dependencies are listed in requirements.txt)

## <a name="features"></a>Features

#### Search 

![Entering search terms](/static/docs/homepage.png)

Clicking the 'Search' button will send the user's inputs to the server and use fuzzywuzzy to process them with fuzzy string comparison. The resulting terms will either be used to query the database for a matching studio or be used as inputs for a Yelp API search request. 

#### Search Results

![Search results](/static/docs/search_results.png)

The search will display the top 10 matching results and show data from the Yelp API request as well as a Google map with a marker for the location of each studio. 

#### Studio Details Page

![Studio details](/static/docs/studio_profile.png)

Clicking on the name of a studio will bring a user to that studio's details page. This page displays information from the Yelp API, a map, and reviews and ratings pulled from a database query. When logged in, users can click the 'Favorite' button to add or remove the studio from their list of favorites saved in the database.

#### Instructor Move Form

![Instructor move form](/static/docs/instructor_move.png)

Users can submit a form if a particular instructor has switched studios. Users enter the name and location of the new studio. These inputs are used to query the database for the studio and then update the instructor's information in the database.

#### Review Form

![Review form](/static/docs/review_form.png)

Users can click the 'Review this studio' button to submit a review with ratings for various aspects of the studios. Their ratings are calculated into the average star ratings that are displayed on the studio details page. 

#### User Profile Page

![User profile page](/static/docs/user_profile.png)

Users can create accounts in order to view a profile page that queries the database to display their personal information, a selection of their reviews, their favorite studios, and their preferences.

#### User Preferences Form

![User preferences form](/static/docs/user_preferences.png)

Users can update their preferences in this form and click 'Update' to adjust their preferences in the database. Each preference is given a weight and used to create a weighted average and an individualized score for each studio. 


## <a name="v2"></a>Version 2.0

The next steps I'd like to take are to streamline my frontend using AngularJS, to hash users' passwords before saving them to the database, and to build out my user preferences feature using a more advanced algorithm.

## <a name="author"></a>Author
Celia Waggoner is a software engineer in San Francisco, CA.

cmwaggoner@gmail.com

www.linkedin.com/in/celiawaggoner