from mongoengine import Document
from mongoengine.fields import *
from mongoengine import Document, EmbeddedDocument
from datetime import datetime

# review document schema
class Reviews(EmbeddedDocument):
    username = StringField(unque=True)
    profile_pic = StringField(default="../images/default_user.png")
    review_text = StringField()
    rating = FloatField(default=0.0)
    created = DateTimeField(default=datetime.utcnow())

# book document schema
class Books(Document):
    book_title = StringField(required=True)
    author = ListField(StringField(), required=True)
    description = StringField(required=True, unique=True, default="")
    genres = ListField(StringField(), required=True)
    cover_image = StringField(required=True, default="../images/default_book.png")
    avg_rating = FloatField(default=0.0) 
    links = DictField()       # {'link name': url}
    personality_index = ListField(FloatField(required=True), default=[0.0,0.0,0.0,0.0,0.0])
    reviews = EmbeddedDocumentListField(Reviews)
    cluster = IntField(default=0)
    extra_details = DictField()
    created = DateTimeField(default=datetime.utcnow())

    meta = {
        "ordering": ["-created"],
        "reverse": True
    }

# Shelf Schema
class Shelves(EmbeddedDocument):
    shelf_title = StringField(required=True)
    shelved_books = ListField(ReferenceField('Books', dbref=True), default=[])
    shelf_pic = StringField(default="../images/default_bookshelf.png")
    created = DateTimeField(default=datetime.utcnow())

# user document schema
class Users(Document):
    username = StringField(unque=True)
    password = StringField()
    email = EmailField(unique=True)
    profile_pic = StringField(default="../images/default_user.png")
    date_of_birth = DateTimeField()
    description = StringField(default="i am a default user")
    personality_index = ListField(FloatField(required=True), default=[0.0,0.0,0.0,0.0,0.0])
    friends_list = ListField(ReferenceField('self',  dbref=True))
    shelves = EmbeddedDocumentListField(Shelves, default=[
        Shelves(
            shelf_title="Favourite",
            shelf_pic = "../images/favourite.png"
        )
    ], ordering="created", reverse=True)
    created = DateTimeField(default=datetime.utcnow())

    meta = {
        "indexes": ["username", "email"],
        "ordering": ["-created"]
    }