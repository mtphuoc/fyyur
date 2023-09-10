# Imports

import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#object to describe a Venue
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=('venues'))
    def to_dict(self):
        """ Returns a dictinary of vevenuesnues """
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': self.genres.split(','),  # convert string to list
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
        }  
    def __repr__(self):
        return f'<Venue name={self.name}, city={self.city}, state={self.state}, address={self.address}'
    def __getitem__(self, key):
        return getattr(self, key)
    def showsinvenue(self,isPast):         
        results=[]
        shows = Show.query.filter_by(venue_id=self.id)
        today = datetime.datetime.now()
        if isPast:
           results =  shows.filter(Show.start_time < today).all()
        else:
           results =  shows.filter(Show.start_time >= today).all() 
        showlist = []
        for show in results:
            artist = Artist.query.get(show.artist_id)
            show_data = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time),
            }
            showlist.append(show_data)
        return showlist
    def showscount(self,isPast):
        showlist = self.showsinvenue(isPast)
        return len(showlist)
    
#object to describe an artist
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
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref=('artists'))
    def to_dict(self):
        """ Returns a dictinary of artists """
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres.split(','),  # convert string to list
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
        }
    def __getitem__(self, key):
        return getattr(self, key)        
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    def showsofartist(self,isPast):
        shows = Show.query.filter_by(artist_id=self.id)
        today = datetime.datetime.now()
        results =[]
        if isPast:
            results = shows.filter(Show.start_time < today).all()  
        else:
            results = shows.filter(Show.start_time >= today).all() 
        shows_data = []
        for show in results:
            venue = Venue.query.get(show.venue_id)
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time),
            }
            shows_data.append(show_data) 
        
        return shows_data
    def showscount(self,isPast):
        showlist = self.showsofartist(isPast)
        return len(showlist)
#object to describe a Show
class Show(db.Model):
    """ Show Model """
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    #artist id
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    #venue id
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    def __getitem__(self, key):
        return getattr(self, key)        
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
