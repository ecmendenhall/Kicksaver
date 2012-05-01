from google.appengine.ext import db

class Project(db.Model):
    link = db.LinkProperty()
    left = db.IntegerProperty() 
    end = db.DateTimeProperty()
    saved = db.DateTimeProperty()
