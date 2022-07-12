from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()



class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO: Complete

    genres=db.Column(db.ARRAY(db.String))
    website_link=db.Column(db.String(120))
    looking_for_talent=db.Column(db.Boolean, nullable=False, default=False)
    seeking_description=db.Column(db.String())

    #defining relationship with artist
    shows=db.relationship('Shows', backref=db.backref('venue', lazy=True))

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(120))
    looking_for_venue=db.Column(db.Boolean, nullable=False, default=False)
    seeking_description=db.Column(db.String())
    shows=db.relationship('Shows', backref=db.backref('artist', lazy=True))

    #venues=db.relationship('Venue', secondary='shows', backref=db.backref('artists', lazy=True))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO: Complete

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__='shows'
    venue_id= db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='cascade'), primary_key=True)
    artist_id= db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='cascade'), primary_key=True)
    showtime=db.Column(db.DateTime, nullable=False, primary_key=True)



