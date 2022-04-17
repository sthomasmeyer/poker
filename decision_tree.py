from game_elements import Player, Deck

from hand_rankings import check_straight_flush

from models import db, TexasHoldEmPot

# Import Python's [json] module.
import json

def pre_flop_decision():

    active_pot = TexasHoldEmPot.query.first()

    if active_pot.user_pre_flop > active_pot.ai_pre_flop:
        print("CALL")
        ai_commited_chips = int(active_pot.ai_pre_flop)
        user_commited_chips = int(active_pot.user_pre_flop)
        difference = (user_commited_chips - ai_commited_chips)
        ai_commited_chips += difference
        active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
        active_pot.total_chips = json.dumps(ai_commited_chips + user_commited_chips)
        db.session.commit()

        return active_pot.ai_pre_flop

def post_flop_decision():
    pass


def post_turn_decision():
    pass


def post_river_decision():
    pass
