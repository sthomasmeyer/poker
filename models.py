# Import Python's [datetime] module, which...
# supplies classes for manipulating dates and times.
from datetime import datetime

# Import SQLAlchemy from [flask_sqlalchmey].
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.dialects.postgresql import JSON

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

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    capital = db.Column(JSON)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def formatted_date(self):
        """Return a nicely-formatted date."""
        return self.created_at.strftime("%m-%d-%Y, %H:%M%p")

    # This [player_ratings] attribute is *important* because it finalizes...
    # the connection established by the inclusion of the [user_id]...
    # [ForeignKey()] in the "fifa-rating" table. Additionally, the inclusion of...
    # [backref] establishes a biderectional relationship, wherein...
    # the "child" will get a "parent" attribute w/ [many-to-one] semantics.
    texas_hold_em = db.relationship(
        "TexasHoldEm", backref="user", cascade="all, delete-orphan"
    )


class TexasHoldEm(db.Model):
    __tablename__ = "texas_hold_em"

    id = db.Column(db.Integer, primary_key=True)
    user_cards = db.Column(JSON)
    computer_opp_cards = db.Column(JSON)
    flop = db.Column(JSON)
    turn = db.Column(JSON)
    river = db.Column(JSON)
    user_score = db.Column(JSON)
    computer_opp_score = db.Column(JSON)

    # This [user_id] attribute is *important* because it establishes...
    # a connection between the users in our database and the hand they're...
    # involved in. It is a [one-to-many] relationship, meaning that there is...
    # only one user who will play many different hands.
    # In a [one-to-many] relationship, the [ForeignKey()] command...
    # is placed on the "child" table, referencing the "parent[.relationship()]"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    pot = db.relationship(
        "TexasHoldEmPot", backref="texas_hold_em", cascade="all, delete-orphan"
    )


class TexasHoldEmPot(db.Model):
    __tablename__ = "texas_hold_em_pot"

    id = db.Column(db.Integer, primary_key=True)
    total_chips = db.Column(JSON)
    user_pre_flop = db.Column(JSON)
    ai_pre_flop = db.Column(JSON)
    user_post_flop = db.Column(JSON)
    ai_post_flop = db.Column(JSON)
    user_post_turn = db.Column(JSON)
    ai_post_turn = db.Column(JSON)
    user_post_river = db.Column(JSON)
    ai_post_river = db.Column(JSON)

    hand_id = db.Column(db.Integer, db.ForeignKey("texas_hold_em.id"), nullable=False)
