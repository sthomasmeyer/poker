# Import the classes you've created from the [game_elements.py] file.
from game_elements import Player, Card

# Import the functions you've created from the [hand_rankings.py] file.
from hand_rankings import check_straight_flush

# Import Python's [unittest] module.
import unittest

players = []
alt_players = []

player_one = Player("Archer", 1111)
players.append(player_one)
player_two = Player("Cherlene", 1000000000)
players.append(player_two)

player_three = Player("Lana", 4444)
alt_players.append(player_three)
player_four = Player("Cyrill", 700000)
alt_players.append(player_four)

# Generate two hole cards for player_one
ace_of_spades = Card("s", "A")
ace_of_clubs = Card("c", "A")

player_one.hole_cards.append(ace_of_spades)
player_one.hole_cards.append(ace_of_clubs)

# Generate two hole cards for player_two
eight_of_diamonds = Card("d", "8")
king_of_diamonds = Card("d", "K")

player_two.hole_cards.append(eight_of_diamonds)
player_two.hole_cards.append(king_of_diamonds)

# Generate two hole cards for player_three
ace_of_spades = Card("s", "A")
three_of_spades = Card("s", "3")

player_three.hole_cards.append(ace_of_spades)
player_three.hole_cards.append(three_of_spades)

# Generate two hole cards for player_four
ace_of_hearts = Card("h", "A")
queen_of_spades = Card("s", "Q")

player_four.hole_cards.append(ace_of_hearts)
player_four.hole_cards.append(queen_of_spades)

# Generate five community cards
ace_of_hearts = Card("h", "A")
ace_of_diamonds = Card("d", "A")
eight_of_hearts = Card("h", "8")

three_of_clubs = Card("c", "3")

king_of_clubs = Card("c", "K")

# Generate five alternate community cards
two_of_spades = Card("s", "2")
three_of_diamonds = Card("d", "3")
four_of_spades = Card("s", "4")

queen_of_hearts = Card("h", "Q")

five_of_spades = Card("s", "5")

# Append the community cards to each players post_river_hand
for player in players:
    player.post_river_hand.append(ace_of_hearts)
    player.post_river_hand.append(ace_of_diamonds)
    player.post_river_hand.append(eight_of_hearts)
    player.post_river_hand.append(three_of_clubs)
    player.post_river_hand.append(king_of_clubs)

# Don't forget to append the hole cards!
for player in players:
    for card in player.hole_cards:
        player.post_river_hand.append(card)

# Append the alternate community cards to the alt_players hands
for player in alt_players:
    player.post_river_hand.append(two_of_spades)
    player.post_river_hand.append(three_of_diamonds)
    player.post_river_hand.append(four_of_spades)
    player.post_river_hand.append(queen_of_hearts)
    player.post_river_hand.append(five_of_spades)

# Don't forget to append the hole cards!
for player in alt_players:
    for card in player.hole_cards:
        player.post_river_hand.append(card)

class FirstHandRankingSystemTest(unittest.TestCase):
    def test_hand_ranking_system_success(self):
        actual = check_straight_flush(player_one.post_river_hand)
        expected = 119.13
        self.assertEqual(actual, expected)

class SecondHandRankingSystemTest(unittest.TestCase):
    def test_hand_ranking_system_success(self):
        actual = check_straight_flush(player_two.post_river_hand)
        expected = 44.138
        self.assertEqual(actual, expected)

class ThirdHandRankingSystemTest(unittest.TestCase):
    def test_hand_ranking_system_success(self):
        actual = check_straight_flush(player_three.post_river_hand)
        expected = 125
        self.assertEqual(actual, expected)

class FourthHandRankingSystemTest(unittest.TestCase):
    def test_hand_ranking_system_success(self):
        actual = check_straight_flush(player_four.post_river_hand)
        expected = 65
        self.assertEqual(actual, expected)
