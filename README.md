# Pulse

Learn more about the developer: www.linkedin.com/in/celiawaggoner

Pulse is a fullstack web application that helps people discover new workout studios. The app uses the Yelp and Google Maps APIs to display details and locations of workout studios based on a user's search. Users can also create an account in order to review studios and instructors, save their favorite studios, and set weighted preferences in order to view an individualized score for each studio. 

## Table of Contents
* [Technologies Used](#technologiesused)
* [Features](#features)
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

#### Enter seach terms and click the 'Search' button

![Entering search terms](/static/docs/homepage.png)

This button will send the user inputs to the server and process them using fuzzy string comparison. The resulting terms will either be used to query the database for a matching studio or be used as inputs for a Yelp API search request. 

### View search results

The search will display the matching results and show data from the Yelp API request as well as a Google map with a marker for the location of each studio. 

### Studio details page

Clicking on the name of a studio will bring a user to that studio's details page. This page displays information provided by the Yelp API, a map, as well as reviews and ratings infomration pulled from a database query. Users can click the 'Favorite' button to add or remove the studio from their list of favorites which is saved in the database.

### Instructor move form

Users can submit a form if a particular instructor has switched studios. Users enter the name and location of the new studio. These inputs are used to query the database for the studio and then update the instructor's information in the database so that his or her reviews are reflected on the new page.

### Review form

Users can click the 'Review this studio' button to submit a review with ratings for various aspects of the studios. Their ratings are calculated into the average star ratings that are displayed on the studio details page. 

### User profile page

Users can create accounts in order to view a profile page that queries the database to display their personal information, a selection of their reviews, their favorite studios, and their preferences.

### User preferences form

Users can update their preferences in this form in order to update the database. Each preference is given a weight and used to create a weighted average and an individualized score for each studio. 

## <a name="author"></a>Author
Celia Waggoner is a software engineer in San Francisco, CA.

cmwaggoner@gmail.com

www.linkedin.com/in/celiawaggoner