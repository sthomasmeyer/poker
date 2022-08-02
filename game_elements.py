# Import Python's [random] module.
import random

# Import Python's [json] module.
import json

# Import Flask's session feature that adds support for...
# server-side session storage.
from flask import session

# Import SQLAlchemy (db) from the [models.py] file.
from models import db

# This file contains vital game elements, including...
# PLAYERS that can: hold cards and accumulate chips.
# CARDS w/ suits + values that can be revealed.
# A DECK (of cards) that can be: 1) shuffled, 2) dealt, or 3) "burned".
# An ACTION class that can evaluate the strength of a given hand...
# and make a decision to check / call, bet, or fold.


class Player(object):
    def __init__(self, name, stack):
        self.name = name
        # Create a [dealer] attribute w/ a default value of "False"
        self.dealer = False
        self.stack = stack

        self.pre_flop_bet = 0

        # Create a [hand_ranking] attribute that will allow players...
        # to compare the strength of their hand against opponents.
        self.hand_ranking = 0
        # Create a [hole_cards] list to capture the two cards each player is dealt.
        self.hole_cards = []

        # The following attributes are important bc they allow players...
        # to access + evaluate their hands at each critical point in the game.

        # Create a [post_flop_hand] list to capture the five...
        # cards each player has access to after the flop.
        self.post_flop_hand = []
        # Create a [post_turn_hand] list to capture the six...
        # cards each player has access to after the turn.
        self.post_turn_hand = []
        # Create a [post_river_hand] list to capture the seven...
        # cards each player has access to after the river.
        self.post_river_hand = []

    def accept_dealt_card(self, deck):
        self.hole_cards.append(deck.deal_card())
        return self

    def incorporate_flop(self, deck):
        for card in self.hole_cards:
            self.post_flop_hand.append(card)
        for card in deck.flop:
            self.post_flop_hand.append(card)
        return self

    def incorporate_turn(self, deck):
        for card in self.post_flop_hand:
            self.post_turn_hand.append(card)
        self.post_turn_hand.append(deck.turn[0])
        return self

    def incorporate_river(self, deck):
        for card in self.post_turn_hand:
            self.post_river_hand.append(card)
        self.post_river_hand.append(deck.river[0])
        return self

    # Create a function to convert a given list of Card objects...
    # into JSON format.
    def jsonify_cards(self, list_of_cards):
        suits = []
        vals = []

        for card in list_of_cards:
            vals.append(card.value)
            suits.append(card.suit)

        restructured_hand = []

        # Use the [zip()] method to merge [vals] and [suits]...
        # Each "zipped" item, that is appended to [restructured_hand]...
        # is a tuple containing one element from [vals] + one from [suits]...
        # at an equivalent index --> (e.g., ('8', 's')).
        for item in zip(vals, suits):
            restructured_hand.append(item)

        return json.dumps(restructured_hand)

    def show_hole_cards(self):
        for card in self.hole_cards:
            card.reveal()


class Card(object):
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def reveal(self):
        return f"{self.value}{self.suit}"


class Deck(object):
    def __init__(self):
        # Create a [cards] list that will store all 52 instances of...
        # the Card class that are created when we run the [build()] function.
        self.cards = []
        # Create a [flop] list to capture the three "flop" cards.
        self.flop = []
        # Create a [turn] list to capture the "turn" card.
        self.turn = []
        # Create a [river] list to capture the "river" card.
        self.river = []
        # Create a [community_card(s)] list to capture *all* of the community cards.
        self.community_cards = []

        # Execute the [build()] function to generate a 52-card deck.
        self.build()

    def build(self):
        # Construct an initial [for] loop to cycle through each of the four suits...
        # ("\u2660" = spades, "\u2663" = clubs, "\u2665" = hearts, and "\u2666" = diamonds).
        for s in ["\u2660", "\u2666", "\u2663", "\u2665"]:
            # Construct a [for] loop within our outer-loop to cycle through...
            # every value -- from 2 to Ace -- for each one of the four suits.
            for v in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
                # For every single suit-value combination, create an instance...
                # of the Card class + append it to [self.cards].
                self.cards.append(Card(s, v))

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def deal_card(self):
        return self.cards.pop()

    def flop_protocol(self):
        # burn a card first
        self.cards.pop()
        indices = [len(self.cards) - 1, len(self.cards) - 2, len(self.cards) - 3]
        for i in indices:
            self.flop.append(self.cards.pop(i))
        for card in self.flop:
            self.community_cards.append(card)
        return self.flop

    def turn_protocol(self):
        # burn a card first
        self.cards.pop()
        self.turn.append(self.cards.pop())
        for card in self.turn:
            self.community_cards.append(card)
        return self.turn

    def river_protocol(self):
        # burn a card first
        self.cards.pop()
        self.river.append(self.cards.pop())
        for card in self.river:
            self.community_cards.append(card)
        return self.river

    def jsonify_cards(self, list_of_cards):
        suits = []
        vals = []

        for card in list_of_cards:
            vals.append(card.value)
            suits.append(card.suit)

        restructured_hand = []

        for item in zip(vals, suits):
            restructured_hand.append(item)

        return json.dumps(restructured_hand)


class Action(object):
    def __init__(
        self,
        active_pot,
        hand_rank,
        betting_round,
        raise_count,
        ai_commited_chips,
        ai_stack,
        user_commited_chips,
        user_stack,
        pot_val,
    ):
        self.active_pot = active_pot
        # The [hand_rank] attribute will be a number from 9.XYZ to 135...
        # It might contain many *important* decimal places.
        self.hand_rank = hand_rank
        # The [self.tier] attribute is important bc it determines the...
        # probability that a method (call, raise, fold) will be executed.
        # Note, its value will be "five", "four", "three", "two", or "one".
        self.tier = ""
        # There are four betting rounds: [pre_flop, post_flop, post_turn, post_river]
        self.betting_round = betting_round
        # For each round of betting in Texas hold'em, there is...
        # a maximum of one bet and three raises allowed.
        self.raise_count = raise_count
        self.ai_commited_chips = ai_commited_chips
        self.ai_stack = ai_stack
        self.user_commited_chips = user_commited_chips
        self.user_stack = user_stack
        # This [difference] attribute is useful bc it captures the...
        # difference between user_commited_chips and ai_commited_chips...
        # which is a key variable that informs the decision-making process.
        self.difference = user_commited_chips - ai_commited_chips
        self.pot_val = pot_val

    def apply_tier(self):
        # Apply the appropriate [tier]-identifier to hands in the...
        # pre-flop betting round.
        if self.hand_rank <= 9.07 and self.betting_round == "pre_flop":
            self.tier = "five"
        elif (
            self.hand_rank > 9.07
            and self.hand_rank <= 12
            and self.betting_round == "pre_flop"
        ):
            self.tier = "four"
        elif (
            self.hand_rank > 12
            and self.hand_rank <= 14
            and self.betting_round == "pre_flop"
        ):
            self.tier = "three"
        elif (
            self.hand_rank > 14
            and self.hand_rank <= 15
            and self.betting_round == "pre_flop"
        ):
            self.tier = "two"
        elif self.hand_rank > 15 and self.betting_round == "pre_flop":
            self.tier = "one"

        # Apply the appropriate [tier]-identifier to hands in the...
        # post-flop betting round.
        if self.hand_rank <= 13.10 and self.betting_round == "post_flop":
            self.tier = "five"
        elif (
            self.hand_rank > 13.10
            and self.hand_rank <= 25
            and self.betting_round == "post_flop"
        ):
            self.tier = "four"
        elif (
            self.hand_rank > 25
            and self.hand_rank <= 39
            and self.betting_round == "post_flop"
        ):
            self.tier = "three"
        elif (
            self.hand_rank > 39
            and self.hand_rank <= 47
            and self.betting_round == "post_flop"
        ):
            self.tier = "two"
        elif self.hand_rank > 47 and self.betting_round == "post_flop":
            self.tier = "one"

        # Apply the appropriate [tier]-identifier to hands in the...
        # post-turn betting round.
        if self.hand_rank <= 13.10 and self.betting_round == "post_turn":
            self.tier = "five"
        elif (
            self.hand_rank > 13.10
            and self.hand_rank <= 25
            and self.betting_round == "post_turn"
        ):
            self.tier = "four"
        elif (
            self.hand_rank > 25
            and self.hand_rank <= 39
            and self.betting_round == "post_turn"
        ):
            self.tier = "three"
        elif (
            self.hand_rank > 39
            and self.hand_rank <= 47
            and self.betting_round == "post_turn"
        ):
            self.tier = "two"
        elif self.hand_rank > 47 and self.betting_round == "post_turn":
            self.tier = "one"

        # Apply the appropriate [tier]-identifier to hands in the...
        # post-river betting round.
        elif self.hand_rank <= 14 and self.betting_round == "post_river":
            self.tier = "five"
        elif (
            self.hand_rank > 14
            and self.hand_rank <= 25
            and self.betting_round == "post_river"
        ):
            self.tier = "four"
        elif (
            self.hand_rank > 25
            and self.hand_rank <= 39
            and self.betting_round == "post_river"
        ):
            self.tier = "three"
        elif (
            self.hand_rank > 39
            and self.hand_rank <= 47
            and self.betting_round == "post_river"
        ):
            self.tier = "two"
        elif self.hand_rank > 47 and self.betting_round == "post_river":
            self.tier = "one"

    def bet(self):
        # If there has already been one bet and three raises...
        # then betting again is not an option; default to [call].
        if self.raise_count > 3:
            print("It is against the rules to bet.")
            return self.check_or_call()

        # In the following scenario, the ai-opp has decided to either...
        # raise from the small blind position or re-raise over the top...
        # of a bet made by the active user.
        elif (
            self.raise_count <= 3 and self.user_commited_chips > self.ai_commited_chips
        ):
            # Increment the raise count for the current round of betting.
            self.raise_count += 1
            session[self.betting_round + "_raise_count"] += 1

            # If the number of chips required to call the active user's...
            # bet is equal to the number of chips in the ai-opp's stack...
            # then the ai-opp will go all in to call the user's bet.
            if self.difference == self.ai_stack:
                return self.check_or_call()

            # Given the context, adjust the ai-opp's commited chips...
            # the ai-opp's stack, and the total value of the pot before...
            # deciding how much to bet.
            self.ai_commited_chips += self.difference
            self.ai_stack -= self.difference
            updated_pot_val = self.pot_val + self.difference

            # Does the user have enough capital to call the bet? If not...
            # then place a bet that will force the user to go all in.
            if (round(updated_pot_val / 2) >= self.user_stack) and (
                round(updated_pot_val / 2) <= self.ai_stack
            ):
                self.ai_commited_chips += self.user_stack
                self.ai_stack -= self.user_stack
                self.pot_val = updated_pot_val + self.user_stack

            # The ai-opp has enough capital to make the bet, and the...
            # active user has enough to call.
            elif (round(updated_pot_val / 2) <= self.ai_stack) and (
                round(updated_pot_val / 2) <= self.user_stack
            ):
                self.ai_commited_chips += round(updated_pot_val / 2)
                self.ai_stack -= round(updated_pot_val / 2)
                self.pot_val = updated_pot_val + round(updated_pot_val / 2)

            # Does the ai-opp have enough capital to make the bet?
            elif (round(updated_pot_val / 2) > self.ai_stack) and (
                round(updated_pot_val / 2) <= self.user_stack
              ):
                self.ai_commited_chips += self.ai_stack
                self.pot_val = updated_pot_val + self.ai_stack
                self.ai_stack = 0

            session["ai_stack"] = self.ai_stack

            self.active_pot.total_chips = json.dumps(self.pot_val)
            db.session.commit()

            return self.ai_commited_chips

        elif (
            self.raise_count <= 3 and self.user_commited_chips == self.ai_commited_chips
        ):
            # Increment the raise count for the current round of betting.
            self.raise_count += 1
            session[self.betting_round + "_raise_count"] += 1

            # Does the user have enough capital to call the bet? If not...
            # then place a bet that will force the user to go all in.
            if (round(self.pot_val / 2) >= self.user_stack) and (
                round(self.pot_val / 2) <= self.ai_stack
            ):
                self.ai_commited_chips += self.user_stack
                self.ai_stack -= self.user_stack
                self.pot_val = self.pot_val + self.user_stack

            # The ai-opp has enough capital to make the bet, and the...
            # active user has enough to call.
            elif (round(self.pot_val / 2) <= self.ai_stack) and (
                round(self.pot_val / 2) <= self.user_stack
            ):
                self.ai_commited_chips += round(self.pot_val / 2)
                self.ai_stack -= round(self.pot_val / 2)
                self.pot_val = self.pot_val + round(self.pot_val / 2)

            # Does the ai-opp have enough capital to make the bet?
            elif (round(self.pot_val / 2) > self.ai_stack) and (
                round(self.pot_val / 2) <= self.user_stack
            ):
                self.ai_commited_chips += self.ai_stack
                self.pot_val = self.pot_val + self.ai_stack
                self.ai_stack = 0

            session["ai_stack"] = self.ai_stack

            self.active_pot.total_chips = json.dumps(self.pot_val)
            db.session.commit()

            return self.ai_commited_chips

    def check_or_call(self):
        # Check, if possible.
        if self.user_commited_chips == self.ai_commited_chips:
            return self.ai_commited_chips

        # Otherwise, call.
        elif self.user_commited_chips > self.ai_commited_chips:
            self.ai_commited_chips += self.difference
            self.ai_stack -= self.difference

            session["ai_stack"] = self.ai_stack

            self.active_pot.total_chips = json.dumps(self.pot_val + self.difference)
            db.session.commit()

            return self.ai_commited_chips

    def fold(self):
        # The first of these two [if]-statements determines whether...
        # or not the ai-opp has the option to "check" / defer action...
        # If they do then it would be foolish to fold.
        if self.user_commited_chips == self.ai_commited_chips:
            return self.check_or_call()
        # If the ai-opp does *not* have the option to check, then fold.
        elif self.user_commited_chips > self.ai_commited_chips:
            return None

    def decide(self):
        rnum = random.randint(1, 100)
        if self.tier == "five":
            # bet 5% of the time
            if rnum <= 5:
                return self.bet()
            # call 20% of the time
            if rnum > 5 and rnum <= 25:
                return self.check_or_call()
            # fold 75% of the time
            if rnum > 25:
                return self.fold()
        if self.tier == "four":
            # bet 20% of the time
            if rnum <= 20:
                return self.bet()
            # call 60% of the time
            if rnum > 20 and rnum <= 80:
                return self.check_or_call()
            # fold 20% of the time
            if rnum > 80:
                return self.fold()
        if self.tier == "three":
            # bet 45% of the time
            if rnum <= 45:
                return self.bet()
            # call 45% of the time
            if rnum > 45 and rnum <= 90:
                return self.check_or_call()
            # fold 10% of the time
            if rnum > 90:
                return self.fold()
        if self.tier == "two":
            # bet 75% of the time
            if rnum <= 75:
                return self.bet()
            # call 25% of the time
            if rnum > 75:
                return self.check_or_call()
        if self.tier == "one":
            return self.bet()
