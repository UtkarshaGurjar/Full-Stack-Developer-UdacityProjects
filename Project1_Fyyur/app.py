#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Precious50$@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
	
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    upcoming_shows_count = db.Column(db.Integer)
    upcoming_shows = db.Column(db.String())
    past_shows_count = db.Column(db.Integer)
    past_shows = db.Column(db.String())
    shows_venue = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    website = db.Column(db.String(500))
    upcoming_shows_count = db.Column(db.Integer)
    upcoming_shows = db.Column(db.String())
    past_shows_count = db.Column(db.Integer)
    past_shows = db.Column(db.String())
    shows_artist = db.relationship('Show', backref='artist', lazy=True)
	
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
	__tablename__ = 'Show'
	id = db.Column(db.Integer, primary_key=True)
	start_time = db.Column(db.DateTime)
	venue_image_link = db.Column(db.String(500))
	artist_image_link = db.Column(db.String(500))
	venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
	artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
	venue_name = db.relationship('Venue', backref=db.backref('shows', lazy='dynamic'))
	artist_name = db.relationship('Artist', backref=db.backref('shows'))

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  city_state = ''
  data = []
  venue_query = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  for venue in venue_query:
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()

    if city_state == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })
      
    else:
      city_state = venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    search_term = request.form.get('search_term', '')

    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
      "count": len(results),
      "data": [{
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(shows)
      } for v in results]
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    flash('Wrong search, try again')
    return redirect(url_for('venues'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  list_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []

  for show in list_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime('%m/%d/%Y')
		}

    if (show.start_time < datetime.now()):
        #print(past_shows, file=sys.stderr)
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  data = request.form
  try:
    new_venue = Venue(
    genres=data.getlist("genres[]"),
    name=data.get("name"),
    address=data.get("address"),
    city=data.get("city"),
    state=data.get("state"),
    facebook_link=data.get("facebook_link"),
    phone=data.get("phone"),
    website=data.get("website_link"),
    image_link=data.get("image_link")
  )
    Venue.insert(new_venue)
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except SQLAlchemyError as e:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue_query = Venue.query.get(venue_id)
  
  if venue_query:
    Venue.delete(venue_query)
  
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name)
  data=[]

  for artist in artists:
      data.append({
        "id": artist[0],
        "name": artist[1]
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []

  for artist in artists:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.artist_id == artist.id)
      for show in shows:
          if(show.stat_time > datetime.now()):
              num_upcoming_shows += 1;
      data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming_shows
      })
  response={
      "count": len(artists),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  past_shows = []
  upcoming_shows = []

  for show in list_shows:
      venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

      show_add = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_time.strftime('%m/%d/%Y')
          }

      if (show.start_time < datetime.now()):
          #print(past_shows, file=sys.stderr)
          past_shows.append(show_add)
      else:
          print(show_add, file=sys.stderr)
          upcoming_shows.append(show_add)

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()[0]

  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    genres=artist.genres,
    phone=artist.phone,
    facebook_link=artist.facebook_link,
    website=artist.website,
    image_link=artist.image_link,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]

    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website=request.form.get('website')
    artist.image_link=request.form.get('image_link')
    artist.seeking_venue=request.form.get('seeking_venue') == 'True'
    artist.seeking_description=request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).all()[0]

  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    facebook_link=venue.facebook_link,
    website=venue.website,
    image_link=venue.image_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]

    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.address=request.form.get('address')
    venue.phone=request.form.get('phone')
    venue.facebook_link=request.form.get('facebook_link')
    venue.website=request.form.get('website')
    venue.image_link=request.form.get('image_link')
    venue.seeking_talent=request.form.get('seeking_talent') == 'True'
    venue.seeking_description=request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be updated')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  error = False

  try:
    new_artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.getlist('genres'),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link'),
      website=request.form.get('website'),
      seeking_venue=request.form.get('seeking_venue') == 'True',
      seeking_description=request.form.get('seeking_description')
    )
 
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    flash('Artist ' + request.form['name'] + ' successfully listed!')
  else:
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()

  for show in shows:
      artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0]).one()
      venue = db.session.query(Venue.name).filter(Venue.id == show[1]).one()
      data.append({
          "venue_id": show[1],
          "venue_name": venue[0],
          "artist_id": show[0],
          "artist_name": artist[0],
          "artist_image_link": artist[1],
          "start_time": str(show[2])
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
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  form = ShowForm(request.form)

  show = Show(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_time = form.start_time.data
  )

  try:
      db.session.add(show)
      db.session.commit()
      flash('Show successfully added')
  except:
      flash('Error! Show not added')
  finally:
      db.session.close()
  return render_template('pages/shows.html')


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
