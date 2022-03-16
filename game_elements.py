# Import Python's [random] module.
import random

# This file contains vital game elements, including...
# PLAYERS that can: 1) hold cards, 2) check, 3) raise, 4) fold...
# 5) call, and 6) accumulate chips. CARDS w/ suits + values that...
# can be revealed. A DECK (of cards) that can be: 1) shuffled...
# 2) dealt, or 3) "burned".


class Player(object):
    def __init__(self, name, stack):
        self.name = name
        self.stack = "${:,.2f}".format(stack)
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

    # def check(self):

    # def raise(self, amount):

    # def fold(self):

    # def call(self, amount):

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
        # ("s" = spades, "c" = clubs, "h" = hearts, and "d" = diamonds).
        for s in ["s", "c", "h", "d"]:
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

    def reset_deck(self):
        self.cards.clear()
        Deck.build()
        Deck.shuffle()
