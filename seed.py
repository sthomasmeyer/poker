from models import db, User, TexasHoldEm, TexasHoldEmPot
from app import app

db.drop_all()

db.create_all()
