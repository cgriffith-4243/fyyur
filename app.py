#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', passive_deletes='all', lazy=True)

    # added fields based on test data

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', passive_deletes='all', lazy=True)

    # added fields based on test data

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # added fields based on test data
db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  # first retrieve locations that host venues, cities ordered by state
  locations_with_venues = Venue.query.order_by(Venue.state, Venue.city).distinct(Venue.state, Venue.city)
  # For each location, create a json object containing data
  for location in locations_with_venues:
    # find venues that are in the current location
    venues_in_location = Venue.query.order_by(Venue.name).filter_by(state=location.state, city=location.city).all()
    venue_jsons = []
    # create json object for each venue
    for venue in venues_in_location:
      venue_jsons.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
      })
    # location json object
    data.append({
      'city': location.city,
      'state': location.state,
      'venues': venue_jsons
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # retrieve search term and query for matching venues
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  # build json objects containing relevant data for each result
  data = []
  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
    })

  # create response object
  response={
    'count': len(venues),
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  # check if venue id exists. If true, continue. If not, render error page
  if venue:
    all_shows = Show.query.join(Artist, Artist.id == Show.artist_id).filter(Show.venue_id==venue_id).all()
    past_shows = []
    upcoming_shows = []

    for show in all_shows:
      artist_info = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }

      if (show.start_time >= datetime.now()):
        upcoming_shows.append(artist_info)
      else:
        past_shows.append(artist_info)

    data = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows,
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows),
    }
    
    return render_template('pages/show_venue.html', venue=data)
  # if no such artist exists, show error page
  return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  if form.validate():
    try:
      # assign attribute values
      new_venue = Venue(
        name = form.name.data,
        genres = form.genres.data,
        address = form.address.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        website = form.website.data,
        facebook_link = form.facebook_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data
      )
      db.session.add(new_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        # on successful db insert, flash success
        flash('Venue ' + form.name.data + ' was successfully listed!')
        return render_template('pages/home.html')
      else:
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
        return render_template('errors/500.html')
  else:
    for field, errors in form.errors.items():
        for error in errors:
            flash(error + '  Please fix entry and resubmit.')
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  # response body containing the url for the home page
  # note: using redirect(url_for('index')) causes a 405 error
  body = { 'redirect': url_for('index') }
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if not error:
      flash('Venue was successfully deleted!')
    else:
      flash('An error occurred. Venue could not be deleted.')
  return jsonify(body)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.order_by(Artist.name).all()
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # retrieve search term and query for matching venues
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  # build json objects containing relevant data for each result
  data = []
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all())
    })

  # create response object
  response={
    'count': len(artists),
    'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.get(artist_id)
  # check if venue id exists. If true, continue. If not, render error page
  if artist:
    all_shows = Show.query.join(Venue, Venue.id == Show.venue_id).filter(Show.artist_id==artist_id).all()
    past_shows = []
    upcoming_shows = []

    for show in all_shows:
      venue_info = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }

      if (show.start_time >= datetime.now()):
        upcoming_shows.append(venue_info)
      else:
        past_shows.append(venue_info)

    data = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows,
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows),
    }
    
    return render_template('pages/show_artist.html', artist=data)
  # if no such artist exists, show error page
  return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  # if no such artist exists, show error page
  return render_template('errors/404.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if artist:
    if form.validate():
      try:
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        
        db.session.commit()
      except:
        error = True
        db.session.rollback()
      finally:
        db.session.close()
        if not error:
          return redirect(url_for('show_artist', artist_id=artist_id))
        else:
          return render_template('errors/500.html')
    else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(error + '  Please fix entry and resubmit.')
      return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    flash('Artist ID not valid.')
    return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  # if no such venue exists, show error page
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  if venue:
    if form.validate():
      try:
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
      except:
        error = True
        db.session.rollback()
      finally:
        db.session.close()
        if not error:
          return redirect(url_for('show_venue', venue_id=venue_id))
        else:
          return render_template('errors/500.html')
    else:
      for field, errors in form.errors.items():
          for error in errors:
              flash(error + '  Please fix entry and resubmit.')
      return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    flash('Venue ID not valid.')
    return render_template('errors/404.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm(request.form)
  if form.validate():
    try:
      # assign attribute values
      new_artist = Artist(
        name = form.name.data,
        genres = form.genres.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        website = form.website.data,
        facebook_link = form.facebook_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data
      )
      db.session.add(new_artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
      else:
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
        return render_template('errors/500.html')
  else:
    for field, errors in form.errors.items():
        for error in errors:
            flash(error + '  Please fix entry and resubmit.')
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  # response body containing the url for the home page
  # note: using redirect(url_for('index')) causes a 405 error
  body = { 'redirect': url_for('index') }
  try:
    db.session.query(Artist).filter(Artist.id == artist_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if not error:
      flash('Artist was successfully deleted!')
    else:
      flash('An error occurred. Artist could not be deleted.')
  return jsonify(body)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = Show.query.order_by(Show.start_time.desc()).join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  form = ShowForm(request.form)
  if form.validate():
    try:
      # assign attribute values
      new_show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
      )

      db.session.add(new_show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
      else:
        flash('An error occurred. Show could not be listed.')
        return render_template('errors/500.html')
  else:
    for field, errors in form.errors.items():
        for error in errors:
            flash(error + '  Please fix entry and resubmit.')
  return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
