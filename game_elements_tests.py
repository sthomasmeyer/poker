# Import the classes you've created from the [game_elements.py] file.
from game_elements import Deck

# Import Python's [unittest] module.
import unittest

class TestNumCardsInDeck(unittest.TestCase):
    def test_num_cards_in_deck(self):
        # Create a new instance of the 'Deck' class.
        new_deck = Deck()

        # Test to ensure that there are 52 cards in the deck.
        actual = len(new_deck.cards)
        expected = 52
        self.assertEqual(actual, expected)

class TestDeckShuffleMethodPartOne(unittest.TestCase):
    def test_deck_shuffle_method(self):
        # Build a new deck, but DO NOT shuffle it.
        new_deck = Deck()

        # Capture the suit values of the first thirteen cards.
        first_thirteen_cards = new_deck.cards[:13]
        suit_vals = []
        for card in first_thirteen_cards:
            if card.suit == "\u2660":
                suit_vals.append(card.suit)

        # Test to ensure the first thirteen cards are all spades.
        actual = len(suit_vals)
        expected = 13
        self.assertEqual(actual, expected)

class TestDeckShuffleMethodPartTwo(unittest.TestCase):
    def test_deck_shuffle_method(self):
        # Build a new deck (+) shuffle it.
        new_deck = Deck()
        new_deck.shuffle()

        # Capture the suit values of the first thirteen cards.
        first_thirteen_cards = new_deck.cards[:13]
        suit_vals = []
        for card in first_thirteen_cards:
            if card.suit == "\u2660":
                suit_vals.append(card.suit)

        # Test to ensure the first thirteen cards are NOT all spades.
        actual = len(suit_vals)
        expected = 13
        self.assertGreater(expected, actual)

class TestDealCardMethod(unittest.TestCase):
    def test_deal_card_method(self):
        new_deck = Deck()
        new_deck.deal_card()

        actual = len(new_deck.cards)
        expected = 51
        self.assertEqual(actual, expected)
