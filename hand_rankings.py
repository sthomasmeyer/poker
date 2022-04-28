from game_elements import Player, Deck, Card

import json

### The following code is meant to establish [test] classes to play around with. ###

players = []
player_one = Player("Chamath", 1000000000)
players.append(player_one)
player_two = Player("Sacks", 1000000000)
players.append(player_two)

new_deck = Deck()
new_deck.shuffle()

for i in range(1, 3):
    for player in players:
        player.accept_dealt_card(new_deck)

for card in player_one.hole_cards:
    print(f"Chamath: {card.value} of {card.suit}")

for card in player_two.hole_cards:
    print(f"Sacks: {card.value} of {card.suit}")

print(f"Sacks' Pre-flop Hand: {player_two.jsonify_cards(player_two.hole_cards)}")

new_deck.flop_protocol()
for player in players:
    player.incorporate_flop(new_deck)

for card in new_deck.flop:
    print(f"flop: {card.value} of {card.suit}")

print(f"FLOP: {new_deck.jsonify_cards(new_deck.flop)}")

new_deck.turn_protocol()
for player in players:
    player.incorporate_turn(new_deck)

print(f"turn: {new_deck.turn[0].value} of {new_deck.turn[0].suit}")

new_deck.river_protocol()
for player in players:
    player.incorporate_river(new_deck)

print(f"river: {new_deck.river[0].value} of {new_deck.river[0].suit}")

print(
    f"Chamath's Post-river Hand: {player_one.jsonify_cards(player_one.post_river_hand)}"
)

### END of the [test] classes code... COMMENCE hand-rankings ###

OG_CARD_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["s", "c", "h", "d"]
NUMERICAL_VALUES = list(range(2, 15))


def convert_card_values(hand):
    # Create a [suits] list and [vals] list to capture...
    # key info about the given hand. Note, this is important...
    # because the values of "J(ack)" --> "A(ce)" must be...
    # replaced w/ the numbers 11 --> 14 in order for the...
    # hand-ranking system to function properly.
    suits = []
    vals = []

    # Use a [for] loop to cycle through every instance of Card in the...
    # given hand. Leverage the Card class attributes [value] and [suit]...
    # to sort each piece of information into the appropriate list.
    for card in hand:
        vals.append(card.value)
        suits.append(card.suit)

    # Replace "J(ack)" --> "A(ce)" elements w/ appropriate numerical values.
    for i in range(len(vals)):
        if vals[i] == "J":
            vals[i] = "11"
        if vals[i] == "Q":
            vals[i] = "12"
        if vals[i] == "K":
            vals[i] = "13"
        if vals[i] == "A":
            vals[i] = "14"

    # Create a [restructured_hand] list that will be filled w/ the...
    # appropriate numerical values aligned to the same suit as the OG values.
    restructured_hand = []

    # Use the [zip()] method to merge [vals] and [suits]...
    # Each "zipped" item, that is appended to [restructured_hand]...
    # is a tuple containing one element from [vals] + one from [suits]...
    # at an equivalent index --> (e.g., ('8', 's')).
    for item in zip(vals, suits):
        restructured_hand.append(item)

    return restructured_hand


def check_straight_flush(hand):
    # Create a list to capture every suit in the given hand.
    suits_only = []
    # Create a list to capture every value.
    card_vals_only = []
    # Declare a [target_suit] variable to capture the suit...
    # that occurs 5x, if there is one.
    target_suit = ""
    # Create a list to capture the indexed-position of each...
    # instance of the target suit in [suits_only]. Note, this...
    # is *important* because they will be perfectly aligned...
    # to the indexed-positions we need from [card_vals_only].
    target_indices = []
    # Create a list to capture the value of each card that...
    # is involved in the making of the flush. Then, create...
    # one to sort them in descending order.
    suited_card_vals = []
    sorted_suited_card_vals = []

    # Run the given hand through the [convert_card_values] function to...
    # replace the "J(ack)" --> "A(ce)" elements w/ appropriate numerical values.
    altered_hand = convert_card_values(hand)

    # Append appropriate elements to the the value + suit lists.
    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))
        suits_only.append(cards[1])

    # Identify + capture the suit that occurs 5+ times, if there is one.
    for i in suits_only:
        if suits_only.count(i) >= 5:
            target_suit = i

    # If there isn't a suit that occurs 5+ times, then it...
    # is impossible to make a straight flush.
    if target_suit == "":
        return check_four_of_a_kind(hand)

    # Use Python's [enumerate()] method to append appropriate...
    # elements to [target_indices].
    for index, element in enumerate(suits_only):
        if element == target_suit:
            target_indices.append(index)

    # Append appropriate elements to [suited_card_vals].
    for i in target_indices:
        suited_card_vals.append(card_vals_only[i])

    # Sort the suited card values.
    if len(suited_card_vals) > 0:
        sorted_suited_card_vals = sorted(suited_card_vals, reverse=True)

    difference = 0
    dif_one = 0
    dif_two = 0
    dif_three = 0
    dif_four = 0
    dif_five = 0
    final_el_index = len(sorted_suited_card_vals) - 1
    if final_el_index == 4:
        difference = (
            sorted_suited_card_vals[0] - sorted_suited_card_vals[final_el_index]
        )
    elif final_el_index == 5:
        dif_one = (
            sorted_suited_card_vals[0] - sorted_suited_card_vals[final_el_index - 1]
        )
        dif_two = sorted_suited_card_vals[1] - sorted_suited_card_vals[final_el_index]
    elif final_el_index == 6:
        dif_three = (
            sorted_suited_card_vals[0] - sorted_suited_card_vals[final_el_index - 2]
        )
        dif_four = (
            sorted_suited_card_vals[1] - sorted_suited_card_vals[final_el_index - 1]
        )
        dif_five = sorted_suited_card_vals[2] - sorted_suited_card_vals[final_el_index]

    if sorted_suited_card_vals[0:5] == [14, 13, 12, 11, 10]:
        print(f"ROYAL FLUSH: {sorted_suited_card_vals}")
        score = 135
        return score
    elif (
        sorted_suited_card_vals[0] == 14
        and sorted_suited_card_vals[final_el_index] == 2
        and sorted_suited_card_vals[final_el_index - 1] == 3
        and sorted_suited_card_vals[final_el_index - 2] == 4
        and sorted_suited_card_vals[final_el_index - 3] == 5
    ):
        print(f"STRAIGHT FLUSH (A-5): {sorted_suited_card_vals}")
        score = 125
        return score
    elif difference == 4:
        print(f"STRAIGHT FLUSH: {sorted_suited_card_vals}")
        # MAX straight-flush score = 134.XYZ
        score = 120 + sorted_suited_card_vals[0]
        return score
    elif dif_one == 4 or dif_three == 4:
        print(f"STRAIGHT FLUSH: {sorted_suited_card_vals[0:5]}")
        score = 120 + sorted_suited_card_vals[0]
        return score
    elif dif_two == 4 or dif_four == 4:
        print(f"STRAIGHT FLUSH: {sorted_suited_card_vals[1:6]}")
        score = 120 + sorted_suited_card_vals[1]
        return score
    elif dif_five == 4:
        print(f"STRAIGHT FLUSH: {sorted_suited_card_vals[2:7]}")
        score = 120 + sorted_suited_card_vals[2]
        return score
    else:
        return check_four_of_a_kind(hand)


def check_four_of_a_kind(hand):
    quads = []
    card_list = []
    # The four-of-a-kind is based on values, rather than suits...
    # It is only necessary to capture the given hand's values.
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    for i in sorted_card_vals:
        if sorted_card_vals.count(i) == 4:
            quads.append(i)
        else:
            card_list.append(i)

    if len(quads) > 0:
        print(f"Quads: {quads}")
        print(f"Remaining Cards: {card_list}")
        # MAX four-of-a-kind score = 119.XYZ
        score = 105 + (quads[0] + card_list[0] / 100)
        return score
    else:
        return check_full_house(hand)


def check_full_house(hand):
    three_of_a_kind = []
    two_of_a_kind = []
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    for i in sorted_card_vals:
        if sorted_card_vals.count(i) == 3:
            three_of_a_kind.append(i)
        elif sorted_card_vals.count(i) == 2:
            two_of_a_kind.append(i)

    if len(three_of_a_kind) > 0 and len(two_of_a_kind) > 0:
        print(f"Tres: {three_of_a_kind}")
        print(f"Dos: {two_of_a_kind}")
        # MAX full-house score = 104.XYZ
        score = 90 + (three_of_a_kind[0] + two_of_a_kind[0] / 100)
        return score
    else:
        return check_flush(hand)


def check_flush(hand):
    suits_only = []
    card_vals_only = []
    target_suit = ""
    target_indices = []
    suited_card_vals = []
    sorted_suited_card_vals = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))
        suits_only.append(cards[1])

    for i in suits_only:
        if suits_only.count(i) >= 5:
            target_suit = i

    if target_suit == "":
        return check_straight(hand)

    for index, element in enumerate(suits_only):
        if element == target_suit:
            target_indices.append(index)

    for i in target_indices:
        suited_card_vals.append(card_vals_only[i])

    if len(suited_card_vals) > 0:
        sorted_suited_card_vals = sorted(suited_card_vals, reverse=True)
        print(f"FLUSH: {sorted_suited_card_vals}")
        # MAX flush score = 89.XYZ
        score = 75 + (
            sorted_suited_card_vals[0]
            + sorted_suited_card_vals[1] / 100
            + sorted_suited_card_vals[2] / 1000
            + sorted_suited_card_vals[3] / 10000
            + sorted_suited_card_vals[4] / 100000
        )
        return score


def check_straight(hand):
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        # Only add unique values.
        if int(cards[0]) not in card_vals_only:
            card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    difference = 0
    dif_one = 0
    dif_two = 0
    dif_three = 0
    dif_four = 0
    dif_five = 0
    final_el_index = len(sorted_card_vals) - 1
    if final_el_index < 4:
        return check_three_of_a_kind(hand)
    elif final_el_index == 4:
        difference = sorted_card_vals[0] - sorted_card_vals[final_el_index]
    elif final_el_index == 5:
        dif_one = sorted_card_vals[0] - sorted_card_vals[final_el_index - 1]
        dif_two = sorted_card_vals[1] - sorted_card_vals[final_el_index]
    elif final_el_index == 6:
        dif_three = sorted_card_vals[0] - sorted_card_vals[final_el_index - 2]
        dif_four = sorted_card_vals[1] - sorted_card_vals[final_el_index - 1]
        dif_five = sorted_card_vals[2] - sorted_card_vals[final_el_index]

    if difference == 4:
        print(f"STRAIGHT: {sorted_card_vals}")
        # MAX straight score = 74.XYZ
        score = 60 + sorted_card_vals[0]
        return score
    elif (
        sorted_card_vals[0] == 14
        and sorted_card_vals[final_el_index] == 2
        and sorted_card_vals[final_el_index - 1] == 3
        and sorted_card_vals[final_el_index - 2] == 4
        and sorted_card_vals[final_el_index - 3] == 5
    ):
        print(f"STRAIGHT (A-5): {sorted_card_vals}")
        score = 65
        return score
    elif dif_one == 4 or dif_three == 4:
        print(f"STRAIGHT: {sorted_card_vals[0:5]}")
        score = 60 + sorted_card_vals[0]
        return score
    elif dif_two == 4 or dif_four == 4:
        print(f"STRAIGHT: {sorted_card_vals[1:6]}")
        score = 60 + sorted_card_vals[1]
        return score
    elif dif_five == 4:
        print(f"STRAIGHT: {sorted_card_vals[2:7]}")
        score = 60 + sorted_card_vals[2]
        return score

    else:
        return check_three_of_a_kind(hand)


def check_three_of_a_kind(hand):
    trips = []
    card_list = []
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    for i in sorted_card_vals:
        if sorted_card_vals.count(i) == 3:
            trips.append(i)
        elif sorted_card_vals.count(i) != 3:
            card_list.append(i)

    if len(trips) > 0:
        print(f"Trips: {trips}")
        print(f"Remaining Cards: {card_list}")
        # MAX three-of-a-kind score = 59.XYZ
        score = 45 + (trips[0] + card_list[0] / 100 + card_list[1] / 1000)
        return score
    else:
        return check_two_pair(hand)


def check_two_pair(hand):
    pairs = []
    card_list = []
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    for i in sorted_card_vals:
        if sorted_card_vals.count(i) == 2 and len(pairs) < 4:
            pairs.append(i)
        elif sorted_card_vals.count(i) == 2 and len(pairs) == 4:
            card_list.append(i)
        elif sorted_card_vals.count(i) == 1:
            card_list.append(i)

    if len(pairs) >= 4:
        print(f"TWO-PAIR: {pairs}")
        print(f"Remaining cards: {card_list}")
        # MAX two-pair score = 44.XYZ
        score = 30 + (max(pairs) + min(pairs) / 100 + card_list[0] / 1000)
        return score
    else:
        return check_pair(hand)


def check_pair(hand):
    pair = []
    card_list = []
    card_vals_only = []

    altered_hand = convert_card_values(hand)

    for cards in altered_hand:
        card_vals_only.append(int(cards[0]))

    sorted_card_vals = sorted(card_vals_only, reverse=True)

    for i in sorted_card_vals:
        if sorted_card_vals.count(i) == 2:
            pair.append(i)
        elif sorted_card_vals.count(i) != 2:
            card_list.append(i)

    # The following lines of code are designed to evaluate a...
    # player's pre-flop hand. With this functionality built-in...
    # the hand ranking system is capable of evaluating a hand...
    # at each critical point in a given hand: pre-flop, post-flop...
    # post-turn, and post-river.
    if len(hand) == 2:
        # Initiate pre-flop hand evaluation process.
        if len(pair) == 2:
            print(f"Pre-flop Pair: {pair}")
            # MAX pre-flop pair score = 29
            score = 15 + pair[0]
            return score
        else:
            print(f"Pre-flop High-card: {card_list[0:2]}")
            # MAX pre-flop high-card score = 14.13
            score = card_list[0] + card_list[1] / 100
            return score

    ### This marks the end of the pre-flop hand evaluation code. ###

    if len(pair) == 2:
        print(f"PAIR: {pair}")
        print(f"Un-paired cards: {card_list}")
        # MAX pair score = 29.XYZ
        score = 15 + (
            pair[0] + card_list[0] / 100 + card_list[1] / 1000 + card_list[2] / 10000
        )
        return score
    else:
        print(f"HIGH-CARD: {card_list[0:5]}")
        # MAX high-card score = 14.XYZ
        score = (
            card_list[0]
            + card_list[1] / 100
            + card_list[2] / 1000
            + card_list[3] / 10000
            + card_list[4] / 100000
        )
        return score


for player in players:
    print(f"{player.name}'s pre-flop hand rating: {check_pair(player.hole_cards)}")
    print(
        f"{player.name}'s post-flop hand rating: {check_straight_flush(player.post_flop_hand)}"
    )
    player.hand_ranking = check_straight_flush(player.post_river_hand)
    print(f"{player.hand_ranking} points for {player.name}.")

if player_one.hand_ranking > player_two.hand_ranking:
    print(f"{player_one.name} wins!")
elif player_one.hand_ranking == player_two.hand_ranking:
    print(f"Draw. Split the pot.")
else:
    print(f"{player_two.name} wins!")
