# Import Python's [datetime] module, which...
# supplies classes for manipulating dates and times.
from datetime import datetime

# Import SQLAlchemy from [flask_sqlalchmey].
from flask_sqlalchemy import SQLAlchemy

# Import [bcrypt] password hashing software.
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Declare a variable [db] and set it equal to SQLAlchemy().
db = SQLAlchemy()

# Write a function to properly connect our selected database.
def connect_db(app):

    # Set [db.app] equal to [app]. Remember, [app] = Flask(__name__)...
    # This establishes a connection between SQLAlchemy() and Flask.
    db.app = app

    # The [init_app(app)] callback can be used to initialize an application...
    # for use w/ this database setup. Never use a database in the context of...
    # an application not initialized this way because connections will leak.
    db.init_app(app)


# Use Python's [class] prototype to create a [User] database model...
# wherein we will outline a SQL "users" table...
# that we will be creating, accessing, updating, etc.
class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.Text, unique=True, primary_key=True)
    capital = db.Column(db.Integer, nullable=False, default=0)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def formatted_date(self):
        """Return a nicely-formatted date."""
        return self.created_at.strftime("%m-%d-%Y, %H:%M%p")
