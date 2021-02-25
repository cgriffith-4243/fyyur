# Fyyur

## Fyyur App

Fyyur is a web application for musical venue and artist booking, meant to facilitate the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner. This application can:

1) Creating new venues, artists, and creating new shows.
2) Searching for venues and artists.
3) Learning more about a specific artist or venue.

This application is implemented in Flask and Python, and uses PostgreSQL database for storing, querying, and creating information about artists and venues on Fyyur.

## Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask) if you haven't already.

  ```
  $ cd ~
  $ sudo pip3 install Flask
  ```

To start and run the local development server,

1. Initialize and activate a virtualenv:
  ```
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  ```

2. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

3. Run the development server:
  ```
  $ export FLASK_APP=app
  $ export FLASK_ENV=development # enables debug mode
  $ python3 app.py
  ```

4. Navigate to Home page [http://localhost:5000](http://localhost:5000)

## Authors

Cameron Griffith authored the [`app.py`](./app.py), [`models.py`](./models.py), [`forms.py`](./forms.py), and the application README. Additionally, implemented functionality to edit and delete specific artists, venues, and shows.

The base code for this project was created by [`Udacity`](https://www.udacity.com) as part of the [`Full Stack Web Developer Nanodegree`](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044) program.
