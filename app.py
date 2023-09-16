#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import itertools
import sys
import json
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.secret_key = 'the long secret key of fyyur app'
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  venues = Venue.query.all()

  keyfunc = lambda v: (v['city'], v['state'])
  sorted_venues = sorted(venues, key=keyfunc)
  grouped_venues = itertools.groupby(sorted_venues, key=keyfunc)
  data = [
        {
            'city': key[0],
            'state': key[1],
            'venues': list(data)
        }
        for key, data in grouped_venues]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  print(search_term)
  venues_found = Venue.query.filter(Venue.name.match(f'%{search_term}%')).all()
  formatted_venues = [
    {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(venue.showsinvenue(False))
    }
    for venue in venues_found]
  response = {'count': len(venues_found), 'data': list(formatted_venues)}
  print(formatted_venues)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
    return abort(404)
  data = venue.to_dict()
  past_shows = venue.showsinvenue(True)
  upcomming_shows = venue.showsinvenue(False)
  
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcomming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcomming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  print(form.phone)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    
    try:
        form = VenueForm(request.form)
        if form.validate_on_submit():
          venue = Venue()
          venue.name = request.form['name']
          venue.city = request.form['city']
          venue.state = request.form['state']
          venue.address = request.form['address']
          venue.phone = request.form['phone']
          tmp_genres = request.form.getlist('genres')
          venue.genres = ','.join(tmp_genres)
          venue.facebook_link = request.form['facebook_link']
          venue.image_link = request.form['image_link']
          venue.website_link = request.form['website_link']
          venue.seeking_talent = request.form['seeking_talent']=='y'
          venue.seeking_description = request.form['seeking_description']
        
          db.session.add(venue)
          db.session.commit()
        else:
          error=True
          for field, message in form.errors.items():
            print("Form error")
            flash(field + ' - ' + str(message), 'danger')
            return render_template('forms/new_venue.html', form=form)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
 
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    #venue = Venue.query.filter_by(id=venue_id).first()
    #if venue is None:
    #    return abort(404)
    #try:
    #    venue.delete()
    #    flash(f'Venue {venue.name} was successfully deleted!', 'success')
    #    return redirect(url_for('index'))
    #except:
    #    flash(f'Venue {venue.name} can''t be deleted.', 'danger')
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists(): 
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists_found = Artist.query.filter(
        Artist.name.match(f'%{search_term}%')).all()
    formatted_artists = [{
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': artist.showscount(False)
    }
        for artist in artists_found]
    response = {'count': len(artists_found), 'data': list(formatted_artists)} 
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    data = artist.to_dict()
    past_shows = artist.showsofartist(True)
    upcoming_shows = artist.showsofartist(False)
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_found = Artist.query.get(artist_id)

  artist = {
    'id': artist_found.id,
    'name': artist_found.name,
    'genres': artist_found.genres.split(', '),
    'city': artist_found.city,
    'state': artist_found.state,
    'phone': artist_found.phone,
    'website_link': artist_found.website_link,
    'facebook_link': artist_found.facebook_link,
    'seeking_venue': artist_found.seeking_venue,
    'seeking_description': artist_found.seeking_description,
    'image_link': artist_found.image_link
  }
  form = ArtistForm(formdata=None, data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    artist = db.session.get(Artist,artist_id)

    if artist is None:
        abort(404)

    form = ArtistForm(request.form)
    error = False
    try:
 
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist.genres = ','.join(tmp_genres)
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website_link = request.form['website_link']
        if 'seeking_venue' in request.form:
          print(request.form['seeking_venue'] )
          artist.seeking_venue = request.form['seeking_venue'] == 'y'
        else: 
          artist.seeking_venue = False
        if 'seeking_description' in request.form:
          artist.seeking_description = request.form['seeking_description']
        if form.validate_on_submit():          
          db.session.add(artist)
          db.session.commit()
        else:
          error=True
          for field, message in form.errors.items():
            print("Form error")
            flash(field + ' - ' + str(message), 'danger')
            return render_template('forms/edit_artist.html', form=form,artist=artist)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Artist ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_found = Venue.query.filter_by(id=venue_id).first()

  if venue_found is None:
    abort(404)

  venue = {
    'id': venue_found.id,
    'name': venue_found.name,
    'genres': venue_found.genres.split(', '),
    'address': venue_found.address,
    'city': venue_found.city,
    'state': venue_found.state,
    'phone': venue_found.phone,
    'website_link': venue_found.website_link,
    'facebook_link': venue_found.facebook_link,
    'seeking_talent': venue_found.seeking_talent,
    'seeking_description': venue_found.seeking_description,
    'image_link': venue_found.image_link
  }
  form = VenueForm(formdata=None, data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = db.session.get(Venue,venue_id)

    if venue is None:
        abort(404)

    form = VenueForm(request.form)
    error = False
    try:
      
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      tmp_genres = request.form.getlist('genres')
      venue.genres = ','.join(tmp_genres)
      venue.facebook_link = request.form['facebook_link']
      venue.image_link = request.form['image_link']
      venue.website_link = request.form['website_link']
      if 'seeking_talent' in request.form:
        venue.seeking_talent = request.form['seeking_talent'] == 'y'
      if 'seeking_description' in request.form:
        venue.seeking_description = request.form['seeking_description']
      if form.validate_on_submit(): 
        db.session.add(venue)
        db.session.commit()
      else:
          error=True
          for field, message in form.errors.items():
            print("Form error")
            flash(field + ' - ' + str(message), 'danger')
            return render_template('forms/edit_venue.html', form=form,venue=venue)        
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

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
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist.genres = ','.join(tmp_genres)
        artist.website_link = request.form['website_link']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        if 'seeking_venue' in request.form:
          artist.seeking_venue = request.form['seeking_venue'] == 'y'
        artist.seeking_description = request.form['seeking_description']
        if form.validate_on_submit():
          db.session.add(artist)
          db.session.commit()
        else:
          error=True
          for field, message in form.errors.items():
            print("Form error")
            flash(field + ' - ' + str(message), 'danger')
            return render_template('forms/new_artist.html', form=form)     
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        else:
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  data = []
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  choose_option = (0, 'Select...')
  form.artist_id.choices = [choose_option]
  form.artist_id.choices += [(artist.id, artist.name) for artist in Artist.query.order_by(Artist.name.asc()).all()]
  form.venue_id.choices = [choose_option]
  form.venue_id.choices += [(venue.id, venue.name) for venue in Venue.query.order_by(Venue.name.asc()).all()]
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    data = Show()
   
    data.artist_id=artist_id
    data.venue_id=venue_id
    data.start_time=start_time
          
    db.session.add(data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        flash('An error occured. Venue ' +
        request.form['artist_id'] + ' Could not be listed!')
    else:
        flash('Show ' + request.form['artist_id'] + ' was successfully listed!')
    return render_template('pages/home.html')
    
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
