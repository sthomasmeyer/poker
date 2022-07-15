# Import Python's [os] module, which provides functions for interacting w/ the operating system.
import os

# Import Python's [importLib] module.
import importlib

# Import Python's [json] module.
import json

# Import Python's [math] module.
import math

# Import Flask itself, from [flask], and import all of the Flask features...
# (i.e., render_template, request) that you will be using in this application.
from flask import Flask, request, render_template, redirect, flash, session

# Import Flask-CORS, an extension for handling Cross Origin Resource Sharing.
from flask_cors import CORS

# Import SQLAlchemy (db), the [connect_db] function, and the classes you've created from the [models.py] file.
from models import bcrypt, db, connect_db, User, TexasHoldEm, TexasHoldEmPot

# Import the forms you've created from the [forms.py] file.
from forms import (
    UserLoginForm,
    CreateAccountForm,
    UpdateAccountForm,
)

# Import the classes you've created from the [game_elements.py] file.
from game_elements import Player, Deck, Card, Action

# Import the functions you've created from the [hand_rankings.py] file.
from hand_rankings import (
    check_straight_flush,
    check_pair,
    check_three_of_a_kind,
    check_four_of_a_kind,
)

# Import sensitive information from the [secrets.py] file.
import secrets

importlib.reload(secrets)
new_secret_key = secrets.SUPER_SECRET_KEY
dev_db_connection = secrets.DEVELOPMENT_DB
test_db_connection = secrets.TEST_DB

app = Flask(__name__, template_folder="Templates", static_folder="Static")
CORS(app)

# Config(ure) the application's database URI and secret key...
# Use the [os.environ] command to access the environmental variables...
# then, employ Python's [get()] method to capture the values associated...
# w/ "DATABASE_URL" and "SECRET_KEY".
# Note, default values are provided in both dev and testing environments...
# which will connect this application to a local PostgreSQL database...
# It is important to do this *before* calling the [connect_db(app)] function.

if (os.environ.get("FLASK_ENV") == "development"):
    print(f"This app is deployed in a {os.environ.get('FLASK_ENV')} environment.")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", dev_db_connection
    )

    app.config["SECRET_KEY"] = new_secret_key

elif (os.environ.get("FLASK_ENV") == "testing"):
    print(f"This app is deployed in a {os.environ.get('FLASK_ENV')} environment.")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", test_db_connection
    )

    app.config["SECRET_KEY"] = new_secret_key

else: 
    print("This app is deployed on a Heroku server.")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace(
        "://", "ql://"
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# If Flask-SQLAlchemy's Track Modifications feature is set to [True]...
# then it will track modifications of objects and emit signals...
# This requires extra memory, and should be disabled if not needed.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Setting SQLAlchemy's Echo feature to True will log all...
# statements + [repr()] of their parameter lists to...
# the default log handler, typically [sys.stdout] for output.
# app.config["SQLALCHEMY_ECHO"] = True

# Call this function from [models.py] to connect the database we've selected.
connect_db(app)

# The [create_all()] command creates all tables from the given model class(es).
# db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    """Display a landing page [base.html], where users will log in or create a new account."""

    form = UserLoginForm()

    ### CRITICAL ERROR --> if a user inputs an incorrect username and / or password...
    # direct them to the create account page. 

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

        if (not existing_user):
            flash("There is no account associated with that username.")
            return redirect("/")

        if (
            existing_user.username == candidate.username
            and bcrypt.check_password_hash(existing_user.password, candidate.password)
            == True
        ):
            user_id = existing_user.id

            # If a user logs in successfully, store their username in...
            # session storage to keep track of which specific user is logged in.
            session["user_id"] = user_id

            # Reward users w/ +25 capital on successful login.
            user_capital = existing_user.capital
            print(f"User capital status: {user_capital}")
            if user_capital == None:
                user_capital = 25
                existing_user.capital = json.dumps(user_capital)
            else:
                int_user_capital = int(user_capital)
                int_user_capital += 25
                existing_user.capital = json.dumps(int_user_capital)
            db.session.commit()

            return redirect(f"/user/{user_id}")

        elif (
            existing_user.username == candidate.username
            and bcrypt.check_password_hash(existing_user.password, candidate.password)
            == False
        ):
            flash("Incorrect password.")
            return redirect("/")

    return render_template("base.html", form=form)


@app.route("/create_account", methods=["GET", "POST"])
def register():
    """Direct new users to the account registration form."""

    form = CreateAccountForm()

    if form.validate_on_submit():
        data = {
            k: v
            for k, v in form.data.items()
            if k != "csrf_token" and k != "confirm_password"
        }

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

    session["ai_stack"] = 100

    return render_template("successful_login.html", user=user)


@app.route("/update/user/<int:user_id>", methods=["GET", "POST"])
def update(user_id):
    user = User.query.get_or_404(user_id)

    if session["user_id"] != user_id:
        flash("Access denied.")
        return redirect("/")

    form = UpdateAccountForm()

    if form.validate_on_submit():

        users = User.query.all()

        if request.form["username"] != user.username:
            for existing_user in users:
                if existing_user.username == request.form["username"]:
                    flash("An account associated with that username already exists.")
                    return redirect(f"/update/user/{user_id}")

        if request.form["email"] != user.email:
            for existing_user in users:
                if existing_user.email == request.form["email"]:
                    flash(
                        "An account associated with that email address already exists."
                    )
                    return redirect(f"/update/user/{user_id}")

        if (
            request.form["username"] == user.username
            and request.form["email"] == user.email
        ):
            if (
                bcrypt.check_password_hash(user.password, request.form["password"])
                == True
            ):
                flash("username (+) email address (+) password unaltered")
                return redirect(f"/user/{user_id}")
            else:
                updated_pwd = bcrypt.generate_password_hash(request.form["password"])
                updated_utf8_pwd = updated_pwd.decode("utf8")
                user.password = updated_utf8_pwd
                db.session.commit()
                flash("username (+) email address unaltered")
                flash("password updated")
                return redirect(f"/user/{user_id}")

        if (
            request.form["email"] == user.email
            and request.form["username"] != user.username
        ):
            if (
                bcrypt.check_password_hash(user.password, request.form["password"])
                == True
            ):
                user.username = request.form["username"]
                db.session.commit()
                flash("username updated")
                flash("email address (+) password unaltered")
                return redirect(f"/user/{user_id}")
            else:
                updated_pwd = bcrypt.generate_password_hash(request.form["password"])
                updated_utf8_pwd = updated_pwd.decode("utf8")
                user.password = updated_utf8_pwd
                user.username = request.form["username"]
                db.session.commit()
                flash("username (+) password updated")
                flash("email address unaltered")
                return redirect(f"/user/{user_id}")

        if (
            request.form["username"] == user.username
            and request.form["email"] != user.email
        ):
            if (
                bcrypt.check_password_hash(user.password, request.form["password"])
                == True
            ):
                user.email = request.form["email"]
                db.session.commit()
                flash("email address updated")
                flash("username (+) password unaltered")
                return redirect(f"/user/{user_id}")
            else:
                updated_pwd = bcrypt.generate_password_hash(request.form["password"])
                updated_utf8_pwd = updated_pwd.decode("utf8")
                user.password = updated_utf8_pwd
                user.email = request.form["email"]
                db.session.commit()
                flash("email address (+) password updated")
                flash("username unaltered")
                return redirect(f"/user/{user_id}")

        if (
            request.form["username"] != user.username
            and request.form["email"] != user.email
        ):
            if (
                bcrypt.check_password_hash(user.password, request.form["password"])
                == True
            ):
                user.username = request.form["username"]
                user.email = request.form["email"]
                db.session.commit()
                flash("username (+) email address updated")
                flash("password unaltered")
                return redirect(f"/user/{user_id}")
            else:
                updated_pwd = bcrypt.generate_password_hash(request.form["password"])
                updated_utf8_pwd = updated_pwd.decode("utf8")
                user.password = updated_utf8_pwd
                user.email = request.form["email"]
                user.username = request.form["username"]
                db.session.commit()
                flash("username (+) email address (+) password updated")
                return redirect(f"/user/{user_id}")

    return render_template("/update_account.html", user=user, form=form)


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
    print(f"AI SessionStorge Chip-count: {ai_stack}")

    # If a user attempts to access another user's game...
    # restart the application (+) flash a helpful message.
    if session["user_id"] != user_id:
        flash("Access denied.")
        return redirect("/user/<int:user_id>")

    # Reset the bet- / raise-counters for each round of betting.
    session["pre_flop_raise_count"] = 0
    session["post_flop_raise_count"] = 0
    session["post_turn_raise_count"] = 0
    session["post_river_raise_count"] = 0

    # For the purposes of this app, there should be one...
    # and only one hand of Texas Hold'em stored in the...
    # database for each user. With that objective in mind...
    # it is important to delete unnecessary data.
    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

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
        print(f"(2a) AI Session POST-blind Chip-count: {ai_stack}")

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
        print(f"(2b) AI Session POST-blind Chip-count: {ai_stack}")

        pot.total_chips = json.dumps(3)

    db.session.add(pot)
    db.session.commit()

    return render_template(
        "texas_hold_em.html",
        user=user,
        players=players,
        flop=flop,
        turn=turn,
        river=river,
    )


# The following routes are "hidden" in the sense that the user...
# will not be aware of their existence. Nevertheless, they are...
# absolutely vital:
# [user_cards] --> GET the active user's cards
# [ai_opp_cards] --> GET the computer's cards
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


@app.route("/texas_hold_em/user_raise", methods=["GET", "POST"])
def user_raise():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    if request.method == "POST":
        betting_round = request.json["round"]
        print("The current betting-round is: " + request.json["round"])

        session[betting_round + "_raise_count"] += 1
        print(session[betting_round + "_raise_count"])

        if betting_round == "pre_flop":
            user_commited_chips = int(active_pot.user_pre_flop)
        elif betting_round == "post_flop":
            if active_pot.user_post_flop:
                user_commited_chips = int(active_pot.user_post_flop)
            else:
                user_commited_chips = 0
        elif betting_round == "post_turn":
            if active_pot.user_post_turn:
                user_commited_chips = int(active_pot.user_post_turn)
            else:
                user_commited_chips = 0
        elif betting_round == "post_river":
            if active_pot.user_post_river:
                user_commited_chips = int(active_pot.user_post_river)
            else:
                user_commited_chips = 0

        raise_val = request.json["bet"]
        print("The active-user bets: " + request.json["bet"])

        user_commited_chips += int(raise_val)
        print(f"Updated user chips commited: {user_commited_chips}")

        adjusted_user_capital = math.trunc(int(user.capital) - int(raise_val))
        user.capital = json.dumps(adjusted_user_capital)

        adjusted_total_chip_count = math.trunc(
            int(active_pot.total_chips) + int(raise_val)
        )
        active_pot.total_chips = json.dumps(adjusted_total_chip_count)

        if betting_round == "pre_flop":
            active_pot.user_pre_flop = json.dumps(user_commited_chips)
            db.session.commit()
            return active_pot.user_pre_flop

        elif betting_round == "post_flop":
            active_pot.user_post_flop = json.dumps(user_commited_chips)
            db.session.commit()
            total_commited_chips = int(active_pot.user_pre_flop) + int(
                active_pot.user_post_flop
            )
            return json.dumps(total_commited_chips)

        elif betting_round == "post_turn":
            active_pot.user_post_turn = json.dumps(user_commited_chips)
            db.session.commit()
            total_commited_chips = (
                int(active_pot.user_pre_flop)
                + int(active_pot.user_post_flop)
                + int(active_pot.user_post_turn)
            )
            return json.dumps(total_commited_chips)

        elif betting_round == "post_river":
            active_pot.user_post_river = json.dumps(user_commited_chips)
            db.session.commit()
            total_commited_chips = (
                int(active_pot.user_pre_flop)
                + int(active_pot.user_post_flop)
                + int(active_pot.user_post_turn)
                + int(active_pot.user_post_river)
            )
            return json.dumps(total_commited_chips)


@app.route("/texas_hold_em/ai_pre_flop_decision", methods=["POST", "GET"])
def ai_pre_flop_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The current number of chips the ai-opp has commited to the pot:
    ai_commited_chips = int(active_pot.ai_pre_flop)
    print(f"Pre-flop AI Commited Chips: {ai_commited_chips}")

    # The current number of chips the active-user has commited to the pot:
    user_commited_chips = int(active_pot.user_pre_flop)
    print(f"Pre-flop User Commited Chips: {user_commited_chips}")

    # The total number of chips in the pot:
    pot_val = int(active_pot.total_chips)
    print(f"Pre-flop Total Pot Val: {pot_val}")

    # Capture the ai-opp's hand from the db. Then, create two instances...
    # of the [Card]-object w/ the captured info (+) store them in a list.
    ai_json_hand = saved_hand.computer_opp_cards
    ai_hand = []
    for card in json.loads(ai_json_hand):
        ai_hand.append(Card(card[1], card[0]))

    # Rank the ai-opp's pre-flop hand. The rank will be a number from...
    # 3.02 (low) to 29 (high)
    ai_hand_rank = check_pair(ai_hand)

    print(f"Pre-flop Hand Rank: {ai_hand_rank}")

    ai_action = Action(
        active_pot,
        ai_hand_rank,
        "pre_flop",
        session["pre_flop_raise_count"],
        ai_commited_chips,
        ai_stack,
        user_commited_chips,
        pot_val,
    )
    ai_action.apply_tier()
    print(f"Pre-flop TIER: {ai_action.tier}")
    ai_final_decision = ai_action.decide()
    if ai_final_decision:
        active_pot.ai_pre_flop = json.dumps(ai_final_decision)
        db.session.commit()

        return active_pot.ai_pre_flop
    else:
        return json.dumps("xoxo")


@app.route("/texas_hold_em/user_pre_flop_call", methods=["GET", "POST"])
def user_pre_flop_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

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


@app.route("/texas_hold_em/user_pre_flop_check", methods=["GET", "POST"])
def user_pre_flop_check():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    return active_pot.user_pre_flop


@app.route("/texas_hold_em/flop", methods=["GET", "POST"])
def get_flop():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.flop


@app.route("/texas_hold_em/ai_post_flop_decision", methods=["POST", "GET"])
def ai_post_flop_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # Capture the number of chips commited by the active-user (+) the ai-opp...
    # If no chips have been commited, then temporarily assign these variables...
    # a value of zero.
    if active_pot.ai_post_flop:
        ai_commited_chips = int(active_pot.ai_post_flop)
    else:
        ai_commited_chips = 0

    if active_pot.user_post_flop:
        user_commited_chips = int(active_pot.user_post_flop)
    else:
        user_commited_chips = 0

    # The total number of chips in the pot:
    pot_val = int(active_pot.total_chips)

    # Capture the ai-opp's hand from the db. Then, create two instances...
    # of the [Card]-object w/ the captured info (+) store them in a list.
    ai_json_hole_cards = saved_hand.computer_opp_cards
    ai_hole_cards = []
    for card in json.loads(ai_json_hole_cards):
        ai_hole_cards.append(Card(card[1], card[0]))
    # Rank the hole cards.
    ai_hole_card_rank = check_pair(ai_hole_cards)

    # Capture the flop from the db (+) store the cards in a list.
    json_flop = saved_hand.flop
    flop = []
    for card in json.loads(json_flop):
        flop.append(Card(card[1], card[0]))
    # Rank the flop, independent of the hole cards.
    flop_rank = check_three_of_a_kind(flop)

    # Combine the ai-opp's hole cards w/ the flop (+) rank their hand.
    ai_post_flop_hand = ai_hole_cards + flop
    ai_post_flop_hand_rank = check_straight_flush(ai_post_flop_hand)

    # If the independently-ranked flop is as strong as the...
    # flop (+) the ai-opp's hole cards, then they "missed", and...
    # should consider the strength of their hand without taking...
    # the community cards into account.
    if round(flop_rank) == round(ai_post_flop_hand_rank):
        ai_hand_rank = ai_hole_card_rank
    elif round(ai_post_flop_hand_rank) > round(flop_rank):
        ai_hand_rank = ai_post_flop_hand_rank

    print(f"Post-flop Hand Rank: {ai_hand_rank}")

    ai_action = Action(
        active_pot,
        ai_hand_rank,
        "post_flop",
        session["post_flop_raise_count"],
        ai_commited_chips,
        ai_stack,
        user_commited_chips,
        pot_val,
    )
    # Use the [apply_tier()] method to assign a strength-level to the...
    # given hand -- the strongest hands are ranked "tier-one" and the...
    # weakest are ranked "tier-five". This is important bc it influences...
    # the likelihood that a method (call, raise, fold) will be called...
    # when the [decide()] method is executed.
    ai_action.apply_tier()
    print(f"Post-flop TIER: {ai_action.tier}")
    ai_final_decision = ai_action.decide()
    print(f"AI-opp Post-flop Bet: {ai_final_decision}")
    # Note the incorporation of [ai_final_decision == 0] in the following...
    # [if]-statement. It is critical bc the [decide()] method of the...
    # [Action]-class will return zero, which is a falsey value in Python...
    # if the ai-opp decides to "check" / defer action.
    if ai_final_decision:
        active_pot.ai_post_flop = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = int(active_pot.ai_pre_flop) + int(
            active_pot.ai_post_flop
        )

        return json.dumps(total_commited_chips)

    elif ai_final_decision == 0:
        active_pot.ai_post_flop = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = int(active_pot.ai_pre_flop) + int(
            active_pot.ai_post_flop
        )

        return json.dumps(total_commited_chips)

    # If the [decide()] method does *not* return zero, as in zero chips...
    # commited, or some other number (indicating a call or raise) then fold.
    else:
        return json.dumps("xoxo")


@app.route("/texas_hold_em/user_post_flop_call", methods=["GET", "POST"])
def user_post_flop_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # Capture the number of chips commited by the active-user (+) the ai-opp...
    # If no chips have been commited, then temporarily assign these variables...
    # a value of zero.
    ai_commited_chips = int(active_pot.ai_post_flop)

    if active_pot.user_post_flop:
        user_commited_chips = int(active_pot.user_post_flop)
    else:
        user_commited_chips = 0

    # Capture the difference between the ai-opp and user commited chips...
    # (+) update the user's number commited to equal their ai-opponent's.
    difference = ai_commited_chips - user_commited_chips
    user_commited_chips += difference

    # Deduct the chips commited by this user-decision to call...
    # from their total chip stack.
    adjusted_user_capital = int(user.capital) - difference
    user.capital = json.dumps(adjusted_user_capital)

    # Update [user-post-flop] and [total_chips] values.
    active_pot.user_post_flop = json.dumps(user_commited_chips)
    active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
    db.session.commit()

    total_commited_chips = int(active_pot.user_pre_flop) + int(
        active_pot.user_post_flop
    )

    return json.dumps(total_commited_chips)


@app.route("/texas_hold_em/user_post_flop_check", methods=["GET", "POST"])
def user_post_flop_check():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # In the post-flop betting round of Texas hold'em a player...
    # can only "check" (defer action) if there have been...
    # NO chips commited by any player.

    # If this route is called, then update the database to...
    # indicate that the active-user has commited ZERO chips.

    active_pot.user_post_flop = json.dumps(0)
    db.session.commit()

    return active_pot.user_post_flop


@app.route("/texas_hold_em/turn", methods=["GET", "POST"])
def get_turn():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.turn


@app.route("/texas_hold_em/ai_post_turn_decision", methods=["GET", "POST"])
def ai_post_turn_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # Capture the number of chips commited by the active-user (+) the ai-opp...
    # If no chips have been commited, then temporarily assign these variables...
    # a value of zero.
    if active_pot.ai_post_turn:
        ai_commited_chips = int(active_pot.ai_post_turn)
    else:
        ai_commited_chips = 0

    if active_pot.user_post_turn:
        user_commited_chips = int(active_pot.user_post_turn)
    else:
        user_commited_chips = 0

    ### Placeholder code to facilitate gameplay until the...
    ## user-initiated 'check' system is operational.
    if not active_pot.ai_post_flop:
        active_pot.ai_post_flop = json.dumps(0)

    # The total number of chips in the pot:
    pot_val = int(active_pot.total_chips)

    # Capture the ai-opp's hand from the db. Then, create two instances...
    # of the [Card]-object w/ the captured info (+) store them in a list.
    ai_json_hole_cards = saved_hand.computer_opp_cards
    ai_hole_cards = []
    for card in json.loads(ai_json_hole_cards):
        ai_hole_cards.append(Card(card[1], card[0]))
    # Rank the hole cards.
    ai_hole_card_rank = check_pair(ai_hole_cards)

    # Capture the flop from the db (+) store the cards in a list.
    json_flop = saved_hand.flop
    flop = []
    for card in json.loads(json_flop):
        flop.append(Card(card[1], card[0]))

    # Capture the turn from the db (+) store the card in a list.
    json_turn = saved_hand.turn
    turn = []
    for card in json.loads(json_turn):
        turn.append(Card(card[1], card[0]))

    # Combine the flop and the turn (+) rank these community cards.
    community_cards = flop + turn
    community_cards_rank = check_four_of_a_kind(community_cards)

    # Combine the ai-opp's hole cards w/ the community cards (+) rank their hand.
    ai_post_turn_hand = ai_hole_cards + flop + turn
    ai_post_turn_hand_rank = check_straight_flush(ai_post_turn_hand)

    # If the independently-ranked community cards are as strong as...
    # the community cards (+) the ai-opp's hole cards, then they "missed"...
    # and should consider the strength of their hand without taking...
    # the community cards into account.
    if round(community_cards_rank) == round(ai_post_turn_hand_rank):
        ai_hand_rank = ai_hole_card_rank
    elif round(ai_post_turn_hand_rank) > round(community_cards_rank):
        ai_hand_rank = ai_post_turn_hand_rank

    print(f"Post-turn Hand Rank: {ai_hand_rank}")

    ai_action = Action(
        active_pot,
        ai_hand_rank,
        "post_turn",
        session["post_turn_raise_count"],
        ai_commited_chips,
        ai_stack,
        user_commited_chips,
        pot_val,
    )
    ai_action.apply_tier()
    print(f"Post-turn TIER: {ai_action.tier}")
    ai_final_decision = ai_action.decide()
    print(f"AI-opp Post-turn Bet: {ai_final_decision}")

    if ai_final_decision:
        active_pot.ai_post_turn = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = (
            int(active_pot.ai_pre_flop)
            + int(active_pot.ai_post_flop)
            + int(active_pot.ai_post_turn)
        )

        return json.dumps(total_commited_chips)

    elif ai_final_decision == 0:
        active_pot.ai_post_turn = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = (
            int(active_pot.ai_pre_flop)
            + int(active_pot.ai_post_flop)
            + int(active_pot.ai_post_turn)
        )

        return json.dumps(total_commited_chips)

    else:
        return json.dumps("xoxo")


@app.route("/texas_hold_em/user_post_turn_call", methods=["GET", "POST"])
def user_post_turn_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    ai_commited_chips = int(active_pot.ai_post_turn)

    if active_pot.user_post_turn:
        user_commited_chips = int(active_pot.user_post_turn)
    else:
        user_commited_chips = 0

    difference = ai_commited_chips - user_commited_chips
    user_commited_chips += difference

    adjusted_user_capital = int(user.capital) - difference
    user.capital = json.dumps(adjusted_user_capital)

    active_pot.user_post_turn = json.dumps(user_commited_chips)
    active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
    db.session.commit()

    total_commited_chips = (
        int(active_pot.user_pre_flop)
        + int(active_pot.user_post_flop)
        + int(active_pot.user_post_turn)
    )

    return json.dumps(total_commited_chips)


@app.route("/texas_hold_em/user_post_turn_check", methods=["GET", "POST"])
def user_post_turn_check():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    active_pot.user_post_turn = json.dumps(0)
    db.session.commit()

    return active_pot.user_post_turn


@app.route("/texas_hold_em/river", methods=["GET", "POST"])
def get_river():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()

    return saved_hand.river


@app.route("/texas_hold_em/ai_post_river_decision", methods=["GET", "POST"])
def ai_post_river_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # Capture the number of chips commited by the active-user (+) the ai-opp...
    # If no chips have been commited, then temporarily assign these variables...
    # a value of zero.
    if active_pot.ai_post_river:
        ai_commited_chips = int(active_pot.ai_post_river)
    else:
        ai_commited_chips = 0

    if active_pot.user_post_river:
        user_commited_chips = int(active_pot.user_post_river)
    else:
        user_commited_chips = 0

    ### Placeholder code to facilitate gameplay until the...
    ## user-initiated 'check' system is operational.
    if not active_pot.ai_post_flop:
        active_pot.ai_post_flop = json.dumps(0)
    if not active_pot.ai_post_turn:
        active_pot.ai_post_turn = json.dumps(0)

    # The total number of chips in the pot:
    pot_val = int(active_pot.total_chips)

    # Capture the ai-opp's hand from the db. Then, create two instances...
    # of the [Card]-object w/ the captured info (+) store them in a list.
    ai_json_hole_cards = saved_hand.computer_opp_cards
    ai_hole_cards = []
    for card in json.loads(ai_json_hole_cards):
        ai_hole_cards.append(Card(card[1], card[0]))
    # Rank the hole cards.
    ai_hole_card_rank = check_pair(ai_hole_cards)

    json_flop = saved_hand.flop
    flop = []
    for card in json.loads(json_flop):
        flop.append(Card(card[1], card[0]))

    json_turn = saved_hand.turn
    turn = []
    for card in json.loads(json_turn):
        turn.append(Card(card[1], card[0]))

    json_river = saved_hand.river
    river = []
    for card in json.loads(json_river):
        river.append(Card(card[1], card[0]))

    # Combine the flop, turn, and river (+) rank these community cards.
    community_cards = flop + turn + river
    community_cards_rank = check_straight_flush(community_cards)

    ai_post_river_hand = ai_hole_cards + flop + turn + river
    ai_post_river_hand_rank = check_straight_flush(ai_post_river_hand)

    # If the independently-ranked community cards are as strong as...
    # the community cards (+) the ai-opp's hole cards, then they "missed"...
    # and should consider the strength of their hand without taking...
    # the community cards into account.
    if round(community_cards_rank) == round(ai_post_river_hand_rank):
        ai_hand_rank = ai_hole_card_rank
    elif round(ai_post_river_hand_rank) > round(community_cards_rank):
        ai_hand_rank = ai_post_river_hand_rank

    print(f"Post-river Hand Rank: {ai_hand_rank}")

    ai_action = Action(
        active_pot,
        ai_hand_rank,
        "post_river",
        session["post_river_raise_count"],
        ai_commited_chips,
        ai_stack,
        user_commited_chips,
        pot_val,
    )
    ai_action.apply_tier()
    print(f"Post-river TIER: {ai_action.tier}")
    ai_final_decision = ai_action.decide()
    print(f"AI-opp Post-river Bet: {ai_final_decision}")

    if ai_final_decision:
        active_pot.ai_post_river = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = (
            int(active_pot.ai_pre_flop)
            + int(active_pot.ai_post_flop)
            + int(active_pot.ai_post_turn)
            + int(active_pot.ai_post_river)
        )

        return json.dumps(total_commited_chips)

    elif ai_final_decision == 0:
        active_pot.ai_post_river = json.dumps(ai_final_decision)
        db.session.commit()
        total_commited_chips = (
            int(active_pot.ai_pre_flop)
            + int(active_pot.ai_post_flop)
            + int(active_pot.ai_post_turn)
            + int(active_pot.ai_post_river)
        )

        return json.dumps(total_commited_chips)

    else:
        return json.dumps("xoxo")


@app.route("/texas_hold_em/user_post_river_call", methods=["GET", "POST"])
def user_post_river_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    ai_commited_chips = int(active_pot.ai_post_river)

    if active_pot.user_post_river:
        user_commited_chips = int(active_pot.user_post_river)
    else:
        user_commited_chips = 0

    difference = ai_commited_chips - user_commited_chips
    user_commited_chips += difference

    adjusted_user_capital = int(user.capital) - difference
    user.capital = json.dumps(adjusted_user_capital)

    active_pot.user_post_river = json.dumps(user_commited_chips)
    active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
    db.session.commit()

    total_commited_chips = (
        int(active_pot.user_pre_flop)
        + int(active_pot.user_post_flop)
        + int(active_pot.user_post_turn)
        + int(active_pot.user_post_river)
    )

    return json.dumps(total_commited_chips)


@app.route("/texas_hold_em/user_post_river_check", methods=["GET", "POST"])
def user_post_river_check():
    user_id = session["user_id"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    active_pot.user_post_river = json.dumps(0)
    db.session.commit()

    return active_pot.user_post_river


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


@app.route("/texas_hold_em/showdown", methods=["GET", "POST"])
def showdown():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    if saved_hand.user_score > saved_hand.computer_opp_score:
        int_pot = int(active_pot.total_chips)
        adjusted_user_capital = math.trunc(int(user.capital) + int_pot)
        user.capital = json.dumps(adjusted_user_capital)
        db.session.commit()

        flash(f"Previous hand: [win]")
        return redirect(f"/texas_hold_em/{user_id}")

    if saved_hand.user_score < saved_hand.computer_opp_score:
        int_pot = int(active_pot.total_chips)
        adjusted_ai_stack = math.trunc(ai_stack + int_pot)
        session["ai_stack"] = adjusted_ai_stack

        flash(f"Previous hand: [loss]")
        return redirect(f"/texas_hold_em/{user_id}")

    if saved_hand.user_score == saved_hand.computer_opp_score:
        int_pot = int(active_pot.total_chips)
        adjusted_user_capital = math.trunc(int(user.capital) + int(int_pot / 2))
        user.capital = json.dumps(adjusted_user_capital)
        adjusted_ai_stack = math.trunc(ai_stack + (int_pot / 2))
        session["ai_stack"] = adjusted_ai_stack
        db.session.commit()

        flash(f"Previous hand: [draw]")
        return redirect(f"/texas_hold_em/{user_id}")

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()
