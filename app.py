# Import Python's [os] module, which provides functions for interacting w/ the operating system.
import os

# Import Python's [json] module.
import json

# Import Python's [random] module.
import random

# Import Flask itself, from [flask], and import all of the Flask features...
# (i.e., render_template, request) that you will be using in this application.
from flask import Flask, jsonify, request, render_template, redirect, flash, session, g

# Import SQLAlchemy (db), the [connect_db] function, and the classes you've created from the [models.py] file.
from models import bcrypt, db, connect_db, User, TexasHoldEm, TexasHoldEmPot

# Import the forms you've created from the [forms.py] file.
from forms import UserLoginForm, CreateAccountForm, TexasHoldEmBet

# Import the classes you've created from the [game_elements.py] file.
from game_elements import Player, Deck, Card

# Import the classes you've created from the [game_elements.py] file.
from hand_rankings import check_straight_flush, check_pair

app = Flask(__name__)

# Config(ure) the application's database URI...
# Use the [os.environ] command to access the environmental variables...
# then, employ Python's [get()] method to capture the value associated...
# w/ "DATABASE_URL". Note, in this instance a default is provided...
# which will connect this application to a local SQL database...
# format --> "postgresql://[user:[password]@[host-name]:[port number]/database_name]"
# It is important to do this *before* calling the [connect_db(app)] function.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:batman@localhost:5432/poker"
)

# If Flask-SQLAlchemy's Track Modifications feature is set to [True]...
# then it will track modifications of objects and emit signals...
# This requires extra memory, and should be disabled if not needed.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Setting SQLAlchemy's Echo feature to True will log all...
# statements + [repr()] of their parameter lists to...
# the default log handler, typically [sys.stdout] for output.
app.config["SQLALCHEMY_ECHO"] = True

# Config(ure) the application's "SECRET_KEY"...
# Use the [os.environ] command to access the environmental variables...
# then, employ Python's [get()] method to capture the value associated...
# w/ "SECRET_KEY". Note, a default value -- "secret" -- is set as well.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")

# Call this function from [models.py] to connect the database we've selected.
connect_db(app)

# db.drop_all()
# The [create_all()] command creates all tables from the given model class(es).
db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    """Display a landing page [base.html], where users will log in or create a new account."""

    form = UserLoginForm()

    if form.validate_on_submit():
        # Create a [data] dictionary object. The value of each key [k] is established...
        # in the [forms.py] file, and the value [v] associated w/ each key is based on user-inputs.
        # Note the code -- [if k != "csrf_token"] -- that ensures we do not add WTForms...
        # built-in [csrf] token to this object.
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        # Use a [for] loop to cycle through and "clean" the [data]...
        # before storing it in the database. Use the [replace] method to remove...
        # whitespace, and the [lower] method to store username (+) email all in lower-case.
        for k in data:
            if k != "csrf_token" and k != "password":
                data[k] = data[k].lower()

        # Create an instance of the [User] class "candidate"...
        # Use the [**] operator to unpack the [data] dictionary...
        # into this instance of [User].
        candidate = User(**data)

        existing_user = User.query.filter_by(username=candidate.username).first()

        if (
            existing_user.username == candidate.username
            and bcrypt.check_password_hash(existing_user.password, candidate.password)
            == True
        ):
            user_id = existing_user.id

            # If a user logs in successfully, store their username in...
            # session storage to keep track of which specific user is logged in.
            session["user_id"] = user_id

            # Reward users w/ +100 capital on successful login.
            user_capital = existing_user.capital
            print(f"User capital status: {user_capital}")
            if user_capital == None:
                user_capital = 100
                existing_user.capital = json.dumps(user_capital)
            else:
                int_user_capital = int(user_capital)
                int_user_capital += 100
                existing_user.capital = json.dumps(int_user_capital)
            db.session.commit()

            return redirect(f"/user/{user_id}")

    return render_template("base.html", form=form)


@app.route("/create_account", methods=["GET", "POST"])
def register():
    """Direct new users to the account registration form."""

    form = CreateAccountForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}

        for k in data:
            if k != "csrf_token" and k != "password":
                data[k] = data[k].lower()

        new_user = User(**data)

        users = User.query.all()

        # Use a [for] loop to cycle through the existing user database...
        # to ensure that the desired username doesn't already exist...
        # If it does, redirect users to the [new_user] registration form...
        # and flash them a helpful message.
        for user in users:
            if user.username == new_user.username:
                flash("An account associated with that username already exists.")
                return redirect("/create_account")

        for user in users:
            if user.email == new_user.email:
                flash("An account associated with that email address already exists.")
                return redirect("/create_account")

        # Use [bcrypt] to generate a "hashed" version of the user's password...
        # This is *important* bc storing it as plaintext in our database...
        # is both unethical and unwise -- as it offers opportunities for bad actors...
        # to exploit this information and potentially cause harm to our users.
        hashed_password = bcrypt.generate_password_hash(new_user.password)
        utf8 = hashed_password.decode("utf8")

        # Set the user's password to be the utf8-hashed version that we generated...
        # It is vital that we do this *before* commiting their info to our databse.
        new_user.password = utf8

        db.session.add(new_user)
        db.session.commit()

        flash(
            f"An account has been created for {new_user.username} at {new_user.formatted_date}."
        )
        return redirect("/")

    else:
        return render_template("create_account.html", form=form)


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def successful_login(user_id):
    user = User.query.get_or_404(user_id)

    # If a user attempts to access another user's profile...
    # restart the application (+) flash a helpful message.
    if session["user_id"] != user_id:
        flash("Access denied.")
        return redirect("/")

    session["ai_stack"] = 888

    return render_template("successful_login.html", user=user)


@app.route("/delete/user/<int:user_id>", methods=["POST"])
def destroy(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/")


@app.route("/texas_hold_em/<int:user_id>", methods=["GET", "POST"])
def play_texas_hold_em(user_id):
    user = User.query.get_or_404(user_id)
    ai_stack = session["ai_stack"]
    print("LEROYYYY JENKINS!!!!")
    print(f"(1) AI SessionStorge Chip-count: {ai_stack}")

    # If a user attempts to access another user's profile...
    # restart the application (+) flash a helpful message.
    if session["user_id"] != user_id:
        flash("Access denied.")
        return redirect("/user/<int:user_id>")

    # For the purposes of this app, there should be one...
    # and only one hand of Texas Hold'em stored in the...
    # database for each user. With that objective in mind...
    # it is important to delete unnecessary data.
    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    form = TexasHoldEmBet()

    # Establish a [players] variable and set it equal to...
    # an empty list. Use it to store each instance of the...
    # Player class that you create for a given game.
    players = []

    # Create an [active_user] instance of the Player class...
    # This is (obviously) the user who is logged-in + actively playing.
    active_user = Player(user.username, int(user.capital))
    players.append(active_user)

    # Create a [computer_opponent] instance of the Player class...
    # This poker-bot is named "Cortana" after the fictional AI in Halo.
    computer_opponent = Player("cortana", ai_stack)
    print(f"Opp Player-instance Stack: {computer_opponent.stack}")
    players.append(computer_opponent)

    # Create an instance of the TexasHoldEm class to store...
    # critical data about the active hand in the database.
    new_game = TexasHoldEm()

    # Create an instance of the Deck class and shuffle the deck.
    new_deck = Deck()
    new_deck.shuffle()

    for i in range(1, 3):
        for player in players:
            player.accept_dealt_card(new_deck)

    new_game.user_cards = active_user.jsonify_cards(active_user.hole_cards)
    new_game.computer_opp_cards = computer_opponent.jsonify_cards(
        computer_opponent.hole_cards
    )

    flop = new_deck.flop_protocol()

    new_game.flop = new_deck.jsonify_cards(new_deck.flop)

    for player in players:
        player.incorporate_flop(new_deck)

    turn = new_deck.turn_protocol()

    new_game.turn = new_deck.jsonify_cards(new_deck.turn)

    for player in players:
        player.incorporate_turn(new_deck)

    river = new_deck.river_protocol()

    new_game.river = new_deck.jsonify_cards(new_deck.river)

    for player in players:
        player.incorporate_river(new_deck)

    active_user.hand_ranking = check_straight_flush(active_user.post_river_hand)
    computer_opponent.hand_ranking = check_straight_flush(
        computer_opponent.post_river_hand
    )

    new_game.user_score = json.dumps(active_user.hand_ranking)
    new_game.computer_opp_score = json.dumps(computer_opponent.hand_ranking)

    new_game.user_id = user_id

    db.session.add(new_game)
    db.session.commit()

    pot = TexasHoldEmPot(hand_id=new_game.id)

    if pot.hand_id % 2 == 0:
        active_user.dealer = True
        # If the user is the dealer, then they are responsible for...
        # the small blind. Deduct one unit from their stack (+) add...
        # it to their pre-flop-bet.

        # These lines update the Player class instance.
        active_user.stack -= 1
        active_user.pre_flop_bet += 1
        # These lines update the database.
        adjusted_user_stack = int(user.capital) - 1
        user.capital = json.dumps(adjusted_user_stack)
        pot.user_pre_flop = json.dumps(1)

        computer_opponent.stack -= 2
        computer_opponent.pre_flop_bet += 2
        pot.ai_pre_flop = json.dumps(2)

        # Commit the computer opp's chip-count (stack) to session storage.
        session["ai_stack"] = computer_opponent.stack
        print(f"(2a) AI SessionStorge Chip-count: {ai_stack}")

        pot.total_chips = json.dumps(3)
    else:
        computer_opponent.dealer = True
        # If the user is not the dealer, then they are responsible for...
        # the big blind. Deduct two units from their stack (+) add...
        # them to their pre-flop-bet.

        active_user.stack -= 2
        active_user.pre_flop_bet += 2

        adjusted_user_stack = int(user.capital) - 2
        user.capital = json.dumps(adjusted_user_stack)
        pot.user_pre_flop = json.dumps(2)

        computer_opponent.stack -= 1
        computer_opponent.pre_flop_bet += 1
        pot.ai_pre_flop = json.dumps(1)

        # Commit the computer opp's chip-count (stack) to session storage.
        session["ai_stack"] = computer_opponent.stack
        print(f"(2b) AI SessionStorge Chip-count: {ai_stack}")

        pot.total_chips = json.dumps(3)

    db.session.add(pot)
    db.session.commit()

    return render_template(
        "texas_hold_em.html",
        user=user,
        form=form,
        players=players,
        flop=flop,
        turn=turn,
        river=river,
    )


# The following routes are "hidden" in the sense that the user...
# will not be aware of their existence. Nevertheless, they are...
# absolutely vital:
# [user_cards] --> GET the active user's cards
# [computer_opp_cards] --> GET the computer's cards
# [pre-flop action] --> POST user action (+) GET the computer's response
# [flop] --> GET the flop
# [post-flop action] --> POST user action (+) GET the computer's response
# [turn] --> GET the turn
# [post-turn action] --> POST user action (+) GET the computer's response
# [river] --> GET the river
# [post-river action] --> POST user action (+) GET the computer's response
# [showdown] --> GET the user (+) the computer opp's score


@app.route("/texas_hold_em/user_cards", methods=["GET", "POST"])
def get_user_hand():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.user_cards


@app.route("/texas_hold_em/ai_opp_cards", methods=["GET", "POST"])
def get_ai_opp_hand():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.computer_opp_cards


@app.route("/texas_hold_em/update/ai_opp_chip_count", methods=["POST", "GET"])
def update_ai_chip_count():
    user_id = session["user_id"]
    ai_opp_stack = session["ai_stack"]

    ai_stack = json.dumps(ai_opp_stack)

    return ai_stack


@app.route("/texas_hold_em/update/user_chip_count", methods=["POST", "GET"])
def update_user_chip_count():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    return user.capital


@app.route("/texas_hold_em/update/pot", methods=["POST", "GET"])
def update_pot():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    return active_pot.total_chips


@app.route("/texas_hold_em/ai_pre_flop_action", methods=["POST", "GET"])
def ai_pre_flop_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    ai_json_hand = saved_hand.computer_opp_cards

    ai_hand = []
    for card in json.loads(ai_json_hand):
        ai_hand.append(Card(card[1], card[0]))

    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    ai_hand_rank = check_pair(ai_hand)

    if ai_hand_rank > 13:
        ai_commited_chips = int(active_pot.ai_pre_flop)
        user_commited_chips = int(active_pot.user_pre_flop)

        difference = user_commited_chips - ai_commited_chips
        ai_commited_chips += difference

        ai_stack -= difference
        session["ai_stack"] = ai_stack

        active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
        active_pot.total_chips = json.dumps(ai_commited_chips + user_commited_chips)
        db.session.commit()

        return active_pot.ai_pre_flop
    else: 
        return json.dumps("xXx")


@app.route("/texas_hold_em/user_pre_flop_call", methods=["GET", "POST"])
def user_pre_flop_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # This [if]-statement ensures that the user-decision to call is reasonable.
    if active_pot.user_pre_flop < active_pot.ai_pre_flop:
        # Capture the current value of commited chips, both for the...
        # active user and their ai-opponent. Convert them to integers.
        user_commited_chips = int(active_pot.user_pre_flop)
        ai_commited_chips = int(active_pot.ai_pre_flop)

        # Capture the difference between the ai-opp and user commited chips...
        # (+) update the user's number commited to equal their ai-opponent's.
        difference = ai_commited_chips - user_commited_chips
        user_commited_chips += difference

        # Deduct the chips commited by this user-decision to call...
        # from their total chip stack.
        adjusted_user_capital = int(user.capital) - difference
        user.capital = json.dumps(adjusted_user_capital)

        # Update [user-pre-flop] and [total_chips] values.
        active_pot.user_pre_flop = json.dumps(user_commited_chips)
        active_pot.total_chips = json.dumps(user_commited_chips + ai_commited_chips)
        db.session.commit()

        return active_pot.user_pre_flop


@app.route("/texas_hold_em/flop", methods=["GET", "POST"])
def get_flop():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.flop


@app.route("/texas_hold_em/turn", methods=["GET", "POST"])
def get_turn():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.turn


@app.route("/texas_hold_em/river", methods=["GET", "POST"])
def get_river():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.river


@app.route("/texas_hold_em/computer_opp_score", methods=["GET", "POST"])
def get_computer_opp_score():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.computer_opp_score


@app.route("/texas_hold_em/user_score", methods=["GET", "POST"])
def get_user_score():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.user_score


@app.route("/texas_hold_em/user_fold/<int:user_id>", methods=["GET", "POST"])
def folded(user_id):
    user = User.query.get_or_404(user_id)
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The user has folded, so the ai-opp wins the pot.
    int_pot = int(active_pot.total_chips)
    adjusted_ai_stack = ai_stack + int_pot
    session["ai_stack"] = adjusted_ai_stack

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [user-fold]")
    return redirect(f"/texas_hold_em/{user_id}")


@app.route("/texas_hold_em/ai_opp_fold", methods=["GET", "POST"])
def opp_folded():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The ai-opp has folded, so user has won this hand.
    int_pot = int(active_pot.total_chips)
    adjusted_user_capital = int(user.capital) + int_pot
    user.capital = json.dumps(adjusted_user_capital)
    db.session.commit()

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [ai-opp-fold]")
    return redirect(f"/texas_hold_em/{user_id}")


@app.route("/texas_hold_em/win/<int:user_id>", methods=["GET", "POST"])
def won_hand(user_id):
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The user has won this hand.
    int_pot = int(active_pot.total_chips)
    adjusted_user_capital = int(user.capital) + int_pot
    user.capital = json.dumps(adjusted_user_capital)
    db.session.commit()

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [win]")
    return redirect(f"/texas_hold_em/{user_id}")


@app.route("/texas_hold_em/loss/<int:user_id>", methods=["GET", "POST"])
def lost_hand(user_id):
    user = User.query.get_or_404(user_id)
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The user has lost, so the ai-opp wins the pot.
    int_pot = int(active_pot.total_chips)
    adjusted_ai_stack = ai_stack + int_pot
    session["ai_stack"] = adjusted_ai_stack

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [loss]")
    return redirect(f"/texas_hold_em/{user_id}")
