#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, redirect, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import db, Venue, Artist, Shows
from datetime import date


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# TODO: Complete
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# Models in models.py
# TODO : Complete
#----------------------------------------------------------------------------#


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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #TODO: Complete
  results=Venue.query.distinct('city','state').all()
  data=[]
  for result in results:
    body={}
    body['city']=result.city
    body['state']=result.state
    venues=[]
    venueResults=Venue.query.filter(Venue.city==result.city, Venue.state==result.state).all()
    for venueResult in venueResults:
      venue={}
      venue["id"]=venueResult.id
      venue["name"]=venueResult.name
      venue["num_upcoming_shows"]=Shows.query.filter(Shows.venue_id==venueResult.id, Shows.showtime>=date.today()).count()
      venues.append(venue)
    body["venues"]=venues
    data.append(body)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # TODO: Complete
  venues=Venue.query.filter(Venue.name.ilike('%'+ request.form.get('search_term') +'%')).all()
  data=[]
  for venue in venues:
    body={}
    body['id']=venue.id
    body['name']=venue.name
    body['num_upcomin_shows']=Shows.query.filter(Shows.venue_id==venue.id, Shows.showtime>=date.today()).count()
    data.append(body)
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  # TODO: Complete
  venue=Venue.query.get(venue_id)
  venue_body={}
  pastShows=[]
  upcomingShows=[]
  venue_body['id']=venue.id
  venue_body['name']=venue.name
  venue_body['genres']=venue.genres
  venue_body['address']=venue.address
  venue_body['city']=venue.city
  venue_body['state']=venue.state
  venue_body['phone']=venue.phone
  venue_body['website']=venue.website_link
  venue_body['facebook_link']=venue.facebook_link
  venue_body['seeking_talent']=venue.looking_for_talent
  if venue.looking_for_talent==True:
    venue_body['seeking_description']=venue.seeking_description
  venue_body['image_link']=venue.image_link

  upcomingShowsData= Shows.query.join(Artist, Artist.id==Shows.artist_id).filter(Shows.venue_id==venue_id, Shows.showtime>=date.today()).all()
  pastShowsData= Shows.query.join(Artist, Artist.id==Shows.artist_id).filter(Shows.venue_id==venue_id, Shows.showtime<date.today()).all()
  for showData in pastShowsData:
    pastShow={}
    pastShow['artist_id']=showData.artist_id
    pastShow['artist_name']=showData.artist.name
    pastShow['artist_image_link']=showData.artist.image_link
    pastShow['start_time']=showData.showtime.strftime('%m/%d/%Y, %H:%M:%S')
    pastShows.append(pastShow)
  
  for showData in upcomingShowsData:
    upcomingShow={}
    upcomingShow['artist_id']=showData.artist_id
    upcomingShow['artist_name']=showData.artist.name
    upcomingShow['artist_image_link']=showData.artist.image_link
    upcomingShow['start_time']=showData.showtime.strftime('%m/%d/%Y, %H:%M:%S')
    upcomingShows.append(upcomingShow)
  venue_body['past_shows']=pastShows
  venue_body['upcoming_shows']=upcomingShows
  venue_body['past_shows_count']=len(pastShows)
  venue_body['upcoming_shows_count']=len(upcomingShows)
  return render_template('pages/show_venue.html', venue=venue_body)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: Complete
  error=False
  body={}

  try:
    if request.form.get('seeking_talent')=='y':
      seekingTalent=True
    else:
      seekingTalent=False
    venue=Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      genres=request.form.getlist('genres'),
      website_link=request.form.get('website_link'),
      looking_for_talent=seekingTalent,
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if error==True:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # TODO: Complete
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error=True  
  finally:
    if error== True:
      flash('An error occured. Venue could not be deleted')
      abort(500)
    else:
      flash('Venue Deleted successfully')
      return jsonify(
        {'sucess': True}
      )


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # TODO Bonus: Complete
  #return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # TODO: Complete
  artists= Artist.query.all()
  data=[]
  for artist in artists:
    body={}
    body['id']=artist.id
    body['name']=artist.name
    data.append(body)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # TODO: Complete
  artists=Artist.query.filter(Artist.name.ilike('%'+ request.form.get('search_term') +'%')).all()
  data=[]
  count=0
  for artist in artists:
    count+=1
    body={}
    body['id']=artist.id
    body['name']=artist.name
    body['num_upcomin_shows']=Shows.query.filter(Shows.artist_id==artist.id, Shows.showtime>=date.today()).count()
    data.append(body)
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.get(1)
  data={}
  data['id']=artist.id
  data['name']=artist.name
  data['genres']=artist.genres
  data['city']=artist.city
  data['state']=artist.state
  data['phone']=artist.phone
  data['facebook_link']=artist.facebook_link
  data['seeking_venue']=artist.looking_for_venue
  if artist.looking_for_venue==True:
    data['seeking_description']=artist.seeking_description
  data['image_link']=artist.image_link
  pastShows=[]
  upcomingShows=[]
  #shows=db.session.query(Shows).join(Artist, Artist.id==Shows.artist_id).filter(Artist.id==1).all()
  upcomingShowsAll=db.session.query(Shows).join(Venue, Venue.id==Shows.venue_id).filter(Shows.artist_id==artist_id, Shows.showtime>=date.today()).all()
  for show in upcomingShowsAll:
    showData={}
    showData['venue_id']=show.venue.id
    showData['venue_name']=show.venue.name
    showData['venue_image_link']=show.venue.image_link
    showData['start_time']=show.showtime.strftime('%m/%d/%Y, %H:%M:%S')
    upcomingShows.append(showData)
  pastShowsAll=db.session.query(Shows).join(Venue, Venue.id==Shows.venue_id).filter(Shows.artist_id==artist_id, Shows.showtime<date.today()).all()
  for show in pastShowsAll:
    showData={}
    showData['venue_id']=show.venue.id
    showData['venue_name']=show.venue.name
    showData['venue_image_link']=show.venue.image_link
    showData['start_time']=show.showtime.strftime('%m/%d/%Y, %H:%M:%S')
    pastShows.append(showData)
  data['past_shows']=pastShows
  data['upcoming_shows']=upcomingShows
  data['past_shows_count']=len(pastShows)
  data['upcoming_shows_count']=len(upcomingShows)
  return render_template('pages/show_artist.html', artist=data)

  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={}
  artistResult=Artist.query.get(artist_id)
  artist={}
  artist['id']=artistResult.id
  artist['name']=artistResult.name
  artist['genres']=artistResult.genres
  artist['address']=artistResult.address
  artist['city']=artistResult.city
  artist['state']=artistResult.state
  artist['phone']=artistResult.phone
  artist['website']=artistResult.website_link
  artist['facebook_link']=artistResult.facebook_link
  artist['seeking_talent']=artistResult.looking_for_talent
  artist['seeking_description']=artistResult.seeking_description
  artist['image_link']=artistResult.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error=False
  try:  
    artist=Artist.query.get(artist_id)
    form=ArtistForm(request.form)
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
    if error==True:
      flash("An error occured")
    else:
      flash("Edit successful")
    return redirect(url_for('show_artist', venue_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueResult=Venue.query.get(venue_id)
  venue={}
  venue['id']=venueResult.id
  venue['name']=venueResult.name
  venue['genres']=venueResult.genres
  venue['address']=venueResult.address
  venue['city']=venueResult.city
  venue['state']=venueResult.state
  venue['phone']=venueResult.phone
  venue['website']=venueResult.website_link
  venue['facebook_link']=venueResult.facebook_link
  venue['seeking_talent']=venueResult.looking_for_talent
  venue['seeking_description']=venueResult.seeking_description
  venue['image_link']=venueResult.image_link
  # TODO: populate form with values from venue with ID <venue_id>
  #
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error=False
  try:  
    venue=Venue.query.get(venue_id)
    form=VenueForm(request.form)
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
    if error==True:
      flash("An error occured")
    else:
      flash("Edit successful")
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error=False
  try: 
    if request.form.get('seeking_venue')=='y':
      seekingVenue=True
    else:
      seekingVenue=False
    artist=Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.getlist('genres'),
      image_link=request.form.get('image_link'),
      website_link=request.form.get('website_link'),
      facebook_link=request.form.get('facebook_link'),
      looking_for_venue=seekingVenue,
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error=True
  finally:
    db.session.close()
    if error==True:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # TODO: COMPLETE
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows=Shows.query.all()
  data=[]
  for show in shows:
    showData={}
    showData['venue_id']=show.venue.id
    showData['venue_name']=show.venue.name
    showData['artist_id']=show.artist.id
    showData['artist_name']=show.artist.name    
    showData['artist_image_link']=show.artist.image_link
    showData['start_time']=show.showtime.strftime('%m/%d/%Y, %H:%M:%S')    
    data.append(showData)
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
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  # TODO: Complete

  error=False
  try:
    show=Shows(
      venue_id=request.form.get('venue_id'),
      artist_id=request.form.get('artist_id'),
      showtime=format_datetime(request.form.get('start_time'))
      )
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == False:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
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
