#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def genre_formatter(genres):
    formatted_genres = genres.replace('{', '').replace('}', '')
    formatted_genres = list(formatted_genres.split(','))
    return formatted_genres


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # DONE: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    all_venues = Venue.query.all()
    venue_locations = Venue.query.with_entities(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()
    print('All venues', venue_locations)
    data = []

    for (city, state) in venue_locations:
        venues = Venue.query.filter(
            Venue.city == city, Venue.state == state).all()
        # join with shows and count upcoming
        print('>>>>>>>>>>>>> \n', venues)
        data.append({
        "city": city,
        "state": state,
        "venues": venues
    })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    name = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike('%'+name+'%')).all()
    response = {
        "count": len(venues),
        "data": venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).first()
    venue.genres = genre_formatter(venue.genres)
    
    upcoming_shows_data = Show.query.join("artist_show").\
        join("venue_show"). \
        add_columns(Artist.name, Artist.image_link, Venue.id). \
        filter(Venue.id == venue_id). \
        filter(Show.start_time >= datetime.now()).all()

    upcoming_shows = []
    for upcoming_show in upcoming_shows_data:
        upcoming_shows.append({
            'artist_id': upcoming_show[0].artist_id,
            'artist_name': upcoming_show[1],
            'artist_image_link': upcoming_show[2],
            'start_time': format_datetime(str(upcoming_show[0].start_time))
        })

    venue.upcoming_shows_count = len(upcoming_shows)
    venue.upcoming_shows = upcoming_shows
    
    
    past_shows_data = Show.query.join("artist_show").\
        join("venue_show"). \
        add_columns(Artist.name, Artist.image_link, Venue.id). \
        filter(Venue.id == venue_id). \
        filter(Show.start_time < datetime.now()).all()

    past_shows = []
    for past_show in past_shows_data:
        past_shows.append({
            'artist_id': past_show[0].artist_id,
            'artist_name': past_show[1],
            'artist_image_link': past_show[2],
            'start_time': format_datetime(str(past_show[0].start_time))
        })

    venue.past_shows_count = len(past_shows)
    venue.past_shows = past_shows

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate():
        try:
            new_venue = Venue(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                address=request.form['address'],
                phone=request.form['phone'],
                genres=request.form['genres'],
                facebook_link=request.form['facebook_link'],
                image_link=request.form['image_link'],
                website_link=request.form['website_link'],
                seeking_talent=True if request.form.get(
                    'seeking_talent') == 'y' else False,
                seeking_description=request.form['seeking_description']
            )
            db.session.add(new_venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('The Venue: ' +
                request.form['name'] + ' was created successfully!')

        # DONE: on unsuccessful db insert, flash an error instead.
        except Exception as e:
            print('>>>>>>>>>>>>>:', e, '||', request.form['genres'])
            flash('An error occurred when creating the venue.')
            db.session.rollback()
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.rollback()

    else:
        for error in form.errors:
            flash(form.errors[error][0])


    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    return render_template('pages/artists.html', artists=all_artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike('%' + search + '%')).all()
    response = {
        "count": len(artists),
        "data": artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    artist.genres = genre_formatter(artist.genres)

    upcoming_shows_data = Show.query.join(Venue).\
      add_columns(Venue.name, Venue.image_link).\
      filter(Show.artist_id == artist_id).\
      filter(Show.start_time >= datetime.now()).all()

    upcoming_shows = []
    for upcoming_show in upcoming_shows_data:
      upcoming_shows.append({
          'venue_id': upcoming_show[0].venue_id,
          'venue_name': upcoming_show[1],
          'venue_image_link': upcoming_show[2],
          'start_time': format_datetime(str(upcoming_show[0].start_time))
      })
      

    artist.upcoming_shows = upcoming_shows
    artist.upcoming_shows_count = len(upcoming_shows)
    
    
    past_shows_datas = Show.query.join(Venue, Show.venue_id == Venue.id).\
      add_columns(Venue.name, Venue.image_link).\
      filter(Show.artist_id == artist_id).\
      filter(Show.start_time < datetime.now()).all()

    past_shows = []
    for past_show in past_shows_datas:
      past_shows.append({
          'venue_id': past_show[0].venue_id,
          'venue_name': past_show[1],
          'venue_image_link': past_show[2],
          'start_time': format_datetime(str(past_show[0].start_time))
      })
    
    artist.past_shows = past_shows
    artist.past_shows_count = len(past_shows)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter(Artist.id == artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = {
            "name": request.form['name'],
            "city": request.form['city'],
            "state": request.form['state'],
            "phone": request.form['phone'],
            "genres": request.form.getlist('genres'),
            "facebook_link": request.form['facebook_link'],
            "image_link": request.form['image_link'],
            "website_link": request.form['website_link'],
            "seeking_venue": True if request.form.get('seeking_venue') == 'y' else False,
            "seeking_description": request.form['seeking_description']
        }
        Artist.query.filter_by(id=artist_id).update(artist)
        db.session.commit()
        flash(request.form['name'] + ' has been updated!')
    except:
        db.session.rollback()
        flash('An error occurred while updating the artist')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = {
                "name": request.form['name'],
                "city": request.form['city'],
                "state": request.form['state'],
                "phone": request.form['phone'],
                "genres": request.form.getlist('genres'),
                "facebook_link": request.form['facebook_link'],
                "image_link": request.form['image_link'],
                "website_link": request.form['website_link'],
                "seeking_talent": True if request.form.get('seeking_talent') == 'y' else False,
                "seeking_description": request.form['seeking_description']
                }
        Venue.query.filter_by(id=venue_id).update(venue)
        db.session.commit()
        flash('Venue has been updated succesifully!')
    except:
        db.session.rollback()
        flash('An error occurred while updating the venue')
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
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                genres=request.form.getlist('genres'),
                image_link=request.form['image_link'],
                facebook_link=request.form['facebook_link'],
                seeking_venue=True if request.form.get(
                    'seeking_venue') == 'y' else False,
                website_link=request.form['website_link'],
                seeking_description=request.form['seeking_description'])
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(request.form['name'] +
                ' was successfully added to artists list!')

            return render_template('pages/home.html')

        except Exception as e:
            print('>>>>>>>>>>>>>>>>>>', e)
            db.session.rollback()
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred when adding the artist.')
        finally:
            db.session.close()
    
    else:
        for error in form.errors:
            flash(form.errors[error][0])
    
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    data = []
    shows = Show.query.join("artist_show").join("venue_show").order_by(Show.start_time.desc()).all()
    for show in shows:
        data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_show.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist_show.name,
        "artist_image_link": show.artist_show.image_link,
        "start_time": format_datetime(str(show.start_time))
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
    # DONE: insert form data as a new Show record in the db, instead
    try:
            show = Show(
                artist_id = request.form['artist_id'],
                venue_id  = request.form['venue_id'],
                start_time= request.form['start_time'])
            db.session.add(show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
    except:
         # DONE: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    app.debug = True
    # port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5000)
