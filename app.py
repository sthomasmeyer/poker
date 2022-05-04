# Import Python's [os] module, which provides functions for interacting w/ the operating system.
import os

# Import Python's [importLib] module.
import importlib

# Import Python's [json] module.
import json

# Import Python's [random] module.
import random

# Import Python's [math] module.
import math

# Import Flask itself, from [flask], and import all of the Flask features...
# (i.e., render_template, request) that you will be using in this application.
from flask import Flask, jsonify, request, render_template, redirect, flash, session, g

# Import SQLAlchemy (db), the [connect_db] function, and the classes you've created from the [models.py] file.
from models import bcrypt, db, connect_db, User, TexasHoldEm, TexasHoldEmPot

# Import the forms you've created from the [forms.py] file.
from forms import (
    UserLoginForm,
    CreateAccountForm,
    UpdateAccountForm,
)

# Import the classes you've created from the [game_elements.py] file.
from game_elements import Player, Deck, Card

# Import the classes you've created from the [game_elements.py] file.
from hand_rankings import check_straight_flush, check_pair, check_three_of_a_kind

# Import sensitive information from the [secrets.py] file.
import secrets

importlib.reload(secrets)
new_secret_key = secrets.SUPER_SECRET_KEY
new_db_connection = secrets.LOCAL_SQL_DB

app = Flask(__name__)

# Config(ure) the application's database URI...
# Use the [os.environ] command to access the environmental variables...
# then, employ Python's [get()] method to capture the value associated...
# w/ "DATABASE_URL". Note, in this instance a default is provided...
# which will connect this application to a local SQL database...
# format --> "postgresql://[user:[password]@[host-name]:[port number]/database_name]"
# It is important to do this *before* calling the [connect_db(app)] function.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", new_db_connection
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
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", new_secret_key)

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

    session["ai_stack"] = 888

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


@app.route("/texas_hold_em/ai_pre_flop_decision", methods=["POST", "GET"])
def ai_pre_flop_action():
    user_id = session["user_id"]
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The current number of chips the ai-opp has commited to the pot:
    ai_commited_chips = int(active_pot.ai_pre_flop)

    # The current number of chips the active-user has commited to the pot:
    user_commited_chips = int(active_pot.user_pre_flop)

    # This [difference] variable represents the number...
    # of chips the ai-opp would have to bet to call.
    difference = user_commited_chips - ai_commited_chips

    # The total number of chips in the pot:
    pot = int(active_pot.total_chips)

    # Capture the ai-opp's hand from the db. Then, create two instances...
    # of the [Card]-object w/ the captured info (+) store them in a list.
    ai_json_hand = saved_hand.computer_opp_cards
    ai_hand = []
    for card in json.loads(ai_json_hand):
        ai_hand.append(Card(card[1], card[0]))

    # Rank the ai-opp's pre-flop hand. The rank will be a number from...
    # 3.02 (low) to 29 (high)
    ai_hand_rank = check_pair(ai_hand)

    # This [if]-statement will trigger the ai-decision path for a...
    # "tier one" hand, ranked [15] or higher.
    if ai_hand_rank > 15:
        # In this case, there is no need to produce a random number...
        # bc the ai-opp will only be raising.
        
        # For each round of betting in Texas hold'em, there is...
        # a maximum of one bet and three raises allowed. This..
        # [if]-statement ensures that the ai-opp can still raise.
        if session["pre_flop_raise_count"] <= 3:
            session["pre_flop_raise_count"] += 1

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "call"-level.
            ai_commited_chips += difference
            ai_stack -= difference
            pot = user_commited_chips + ai_commited_chips

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "raise"-level.
            ai_commited_chips += round(pot / 2)
            ai_stack -= round(pot / 2)
            pot += round(pot / 2)

            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_pre_flop

        # If there has already been one bet and three raises...
        # then the ai-opp is forced to call or fold.
        elif session["pre_flop_raise_count"] > 3:
            ai_commited_chips = int(active_pot.ai_pre_flop)
            ai_commited_chips += difference

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(
                ai_commited_chips + user_commited_chips
            )
            db.session.commit()

            return active_pot.ai_pre_flop

    # This [if]-statement will trigger the ai-decision path for a...
    # "tier two" hand, ranked between [14] and [15].
    if ai_hand_rank > 14 and ai_hand_rank < 15:
        # Generate a random number from 1-100.
        rnum = random.randint(1, 100)
        # If the random number is less-than or equal-to [75], then...
        # the ai-opp will raise. In other words, it will raise...
        # 75% of the time.
        if rnum <= 75:

            if session["pre_flop_raise_count"] <= 3:
                session["pre_flop_raise_count"] += 1

                ai_commited_chips += difference
                ai_stack -= difference
                pot = user_commited_chips + ai_commited_chips

                ai_commited_chips += round(pot / 2)
                ai_stack -= round(pot / 2)
                pot += round(pot / 2)

                session["ai_stack"] = ai_stack

                active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                active_pot.total_chips = json.dumps(pot)
                db.session.commit()

                return active_pot.ai_pre_flop

            elif session["pre_flop_raise_count"] > 3:
                ai_commited_chips = int(active_pot.ai_pre_flop)
                ai_commited_chips += difference

                ai_stack -= difference
                session["ai_stack"] = ai_stack

                active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                active_pot.total_chips = json.dumps(
                    ai_commited_chips + user_commited_chips
                )
                db.session.commit()

                return active_pot.ai_pre_flop

        # If the random number is greater-than [75], then the ai-opp...
        # will call. In other words, it will call 25% of the time.
        if rnum > 75:
            ai_commited_chips = int(active_pot.ai_pre_flop)
            ai_commited_chips += difference

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(
                ai_commited_chips + user_commited_chips
            )
            db.session.commit()

            return active_pot.ai_pre_flop

    # This [if]-statement will trigger the ai-decision path for a...
    # "tier three" hand, ranked [12] to [14].
    elif ai_hand_rank > 12 and ai_hand_rank < 14:
        rnum = random.randint(1, 100)
        # The ai-opp will raise 45% of the time.
        if rnum <= 45:

            if session["pre_flop_raise_count"] <= 3:
                session["pre_flop_raise_count"] += 1

                ai_commited_chips += difference
                ai_stack -= difference
                pot = user_commited_chips + ai_commited_chips

                ai_commited_chips += round(pot / 2)
                ai_stack -= round(pot / 2)
                pot += round(pot / 2)

                session["ai_stack"] = ai_stack

                active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                active_pot.total_chips = json.dumps(pot)
                db.session.commit()

                return active_pot.ai_pre_flop

            elif session["pre_flop_raise_count"] > 3:
                rnum = random.randint(1, 100)
                # If this random number is less-than or equal-to [90], then...
                # the ai-opp will call. In other words, the ai-opp will call...
                # 90% of the time.
                if rnum <= 90:
                    ai_commited_chips = int(active_pot.ai_pre_flop)
                    ai_commited_chips += difference

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(
                        ai_commited_chips + user_commited_chips
                    )
                    db.session.commit()

                    return active_pot.ai_pre_flop
                else:
                    return json.dumps("xoxo")

        # The ai-opp will call 45% of the time.
        if rnum > 45 and rnum < 90:
            ai_commited_chips = int(active_pot.ai_pre_flop)
            ai_commited_chips += difference

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(
                ai_commited_chips + user_commited_chips
            )
            db.session.commit()

            return active_pot.ai_pre_flop

        # The ai-opp will fold 10% of the time.
        if rnum >= 90:
            return json.dumps("xoxo")


    # This [if]-statement will trigger the ai-decision path for a...
    # "tier four" hand, ranked [9.07] to [12].
    elif ai_hand_rank >= 9.07 and ai_hand_rank < 12:
        rnum = random.randint(1, 100)
        # The ai-opp will raise 20% of the time.
        if rnum <= 20:

            if session["pre_flop_raise_count"] <= 3:
                session["pre_flop_raise_count"] += 1

                ai_commited_chips += difference
                ai_stack -= difference
                pot = user_commited_chips + ai_commited_chips

                ai_commited_chips += round(pot / 2)
                ai_stack -= round(pot / 2)
                pot += round(pot / 2)

                session["ai_stack"] = ai_stack

                active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                active_pot.total_chips = json.dumps(pot)
                db.session.commit()

                return active_pot.ai_pre_flop

            elif session["pre_flop_raise_count"] > 3:
                rnum = random.randint(1, 100)
                # If this random number is less-than or equal-to [50], then...
                # the ai-opp will call. In other words, the ai-opp will call...
                # 50% of the time.
                if rnum <= 50:
                    ai_commited_chips = int(active_pot.ai_pre_flop)
                    ai_commited_chips += difference

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(
                        ai_commited_chips + user_commited_chips
                    )
                    db.session.commit()

                    return active_pot.ai_pre_flop
                else:
                    return json.dumps("xoxo")

        # The ai-opp will call 60% of the time.
        if rnum > 20 and rnum < 80:
            ai_commited_chips = int(active_pot.ai_pre_flop)
            ai_commited_chips += difference

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(
                ai_commited_chips + user_commited_chips
            )
            db.session.commit()

            return active_pot.ai_pre_flop

        # The ai-opp will fold 20% of the time.
        if rnum >= 80:
            return json.dumps("xoxo")

    # This [if]-statement will trigger the ai-decision path for a...
    # "tier five" hand, ranked lower than [9.07].
    elif ai_hand_rank < 9.07:
        rnum = random.randint(1, 100)
        # The ai-opp will raise 5% of the time.
        if rnum <= 5:

            if session["pre_flop_raise_count"] <= 3:
                session["pre_flop_raise_count"] += 1

                ai_commited_chips += difference
                ai_stack -= difference
                pot = user_commited_chips + ai_commited_chips

                ai_commited_chips += round(pot / 2)
                ai_stack -= round(pot / 2)
                pot += round(pot / 2)

                session["ai_stack"] = ai_stack

                active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                active_pot.total_chips = json.dumps(pot)
                db.session.commit()

                return active_pot.ai_pre_flop

            elif session["pre_flop_raise_count"] > 3:
                rnum = random.randint(1, 100)
                # If this random number is less-than or equal-to [50], then...
                # the ai-opp will call. In other words, the ai-opp will call...
                # 50% of the time.
                if rnum <= 50:
                    ai_commited_chips = int(active_pot.ai_pre_flop)
                    ai_commited_chips += difference

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(
                        ai_commited_chips + user_commited_chips
                    )
                    db.session.commit()

                    return active_pot.ai_pre_flop
                else:
                    return json.dumps("xoxo")

        # The ai-opp will call 20% of the time.
        if rnum > 5 and rnum < 25:
            ai_commited_chips = int(active_pot.ai_pre_flop)
            ai_commited_chips += difference

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_pre_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(
                ai_commited_chips + user_commited_chips
            )
            db.session.commit()

            return active_pot.ai_pre_flop

        # The ai-opp will fold 75% of the time.
        if rnum >= 25:
            return json.dumps("xoxo")


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

    # This [if]-statement will trigger the ai-decision path for a hand...
    # ranked lower than [14.XYZ], Ace-high. Note, it checks to ensure...
    # that the ai-opp can "check" according to the rules.

    # This game-state (wherein the number of chips commited by both the...
    # ai-opp and the active-user, post-flop, are equal) can only occur if...
    # this is the first opportunity for a given player to act in this round...
    # of betting or if the first player to act decided to check.
    if ai_hand_rank < 14 and ai_commited_chips == user_commited_chips:
        # Generate a random number from 1-100.
        rnum = random.randint(1, 100)
        # If this random number is less-than or equal-to [90], then...
        # the ai-opp will check. In other words, the ai-opp will check...
        # 90% of the time.
        if rnum <= 90:
            # Update the [ai_post_flop] section of the db to equal...
            # the number of chips the ai-opp has commited in this...
            # round of betting. In this case, that number is zero.
            active_pot.ai_post_flop = json.dumps(0)
            db.session.commit()

            # Note, because no bet / raise has occured, it is unnecessary...
            # to update the ai-opp's total chip-count (+) the pot.

            return active_pot.ai_post_flop

        # The ai-opp will raise 10% of the time.
        if rnum > 90:
            # Capture the total number of chips in the pot from the db.
            pot = int(active_pot.total_chips)

            # In this scenario, the ai-opp will make a bet that is...
            # (1/3) the size of the total pot.
            ai_commited_chips += round(pot / 3)
            ai_stack -= round(pot / 3)
            pot += round(pot / 3)

            # Update the ai-opp's total chip-count.
            session["ai_stack"] = ai_stack

            # Update (+) commit changes to the db.
            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_flop

    # If this [if]-statement returns "true", then the ai-opp has a hand...
    # ranked lower than [14.XYZ], Ace-high, and they *cannot* check.
    elif ai_hand_rank < 14 and ai_commited_chips < user_commited_chips:
        # Generate a random number from 1-100.
        rnum = random.randint(1, 100)

        # The ai-opp will fold 85% of the time.
        if rnum <= 85:
            return json.dumps("xoxo")

        # The ai-opp will call 10% of the time.
        if rnum > 85 and rnum <= 95:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_flop

        # The ai-opp will raise 5% of the time.
        if rnum > 95:

            # For each round of betting in Texas hold'em, there is...
            # a maximum of one bet and three raises allowed. This...
            # [if]-statement ensures that the ai-opp can still raise.
            if session["post_flop_raise_count"] <= 3:
                session["post_flop_raise_count"] += 1

            # If there has already been one bet and three raises...
            # then the ai-opp is forced to call or fold.
            elif session["post_flop_raise_count"] > 3:
                rnum = random.randint(1, 100)
                # In this scenario, the ai-opp will call 5% of the time.
                if rnum <= 5:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_flop = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_flop
                else:
                    return json.dumps("xoxo")

            # This [difference] variable represents the number...
            # of chips the ai-opp would have to bet to call.
            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "call"-level.
            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "raise"-level.
            ai_commited_chips += round(updated_pot_val / 2)
            ai_stack -= round(updated_pot_val / 2)
            pot = updated_pot_val + round(updated_pot_val / 2)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_flop

    elif ai_hand_rank > 14 and ai_commited_chips == user_commited_chips:
        rnum = random.randint(1, 100)
        # The ai-opp will raise 65% of the time.
        if rnum <= 65:
            session["post_flop_raise_count"] += 1

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += round(initial_pot_val / 3)
            ai_stack -= round(initial_pot_val / 3)
            pot = initial_pot_val + round(initial_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_flop

        # The ai-opp will check 35% of the time.
        elif rnum > 65:
            active_pot.ai_post_flop = json.dumps(0)
            db.session.commit()

            return active_pot.ai_post_flop

    # If this [if]-statement returns "true", then the ai-opp has a hand...
    # ranked higher than [14.XYZ], Ace-high, and they *cannot* check.
    elif ai_hand_rank > 14 and ai_commited_chips < user_commited_chips:
        rnum = random.randint(1, 100)

        # The ai-opp will fold 10% of the time.
        if rnum <= 10:
            return json.dumps("xoxo")

        # The ai-opp will call 45% of the time.
        elif rnum > 10 and rnum <= 55:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_flop

        # The ai-opp will raise 45% of the time, if possible.
        elif rnum > 55:

            # For each round of betting in Texas hold'em, there is...
            # a maximum of one bet and three raises allowed. This...
            # [if]-statement ensures that the ai-opp can still raise.
            if session["post_flop_raise_count"] <= 3:
                session["post_flop_raise_count"] += 1

            # If there has already been one bet and three raises...
            # then the ai-opp is forced to call or fold.
            elif session["post_flop_raise_count"] > 3:
                rnum = random.randint(1, 100)
                # In this scenario, the ai-opp will call 95% of the time.
                if rnum <= 95:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_flop = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_flop
                else:
                    return json.dumps("xoxo")

            # This [difference] variable represents the number...
            # of chips the ai-opp would have to bet to call.
            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "call"-level.
            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            # These lines of code update the ai-opp's commited...
            # chips (+) the pot to a "raise"-level.
            ai_commited_chips += round(updated_pot_val / 3)
            ai_stack -= round(updated_pot_val / 3)
            pot = updated_pot_val + round(updated_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_flop = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_flop


@app.route("/texas_hold_em/user_post_flop_call", methods=["GET", "POST"])
def user_post_flop_call():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)

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

    # This [if]-statement ensures that the user-decision to call is reasonable.
    if user_commited_chips < ai_commited_chips:
        # Capture the difference between the ai-opp and user commited chips...
        # (+) update the user's number commited to equal their ai-opponent's.
        difference = ai_commited_chips - user_commited_chips
        user_commited_chips += difference

        # Deduct the chips commited by this user-decision to call...
        # from their total chip stack.
        adjusted_user_capital = int(user.capital) - difference
        user.capital = json.dumps(adjusted_user_capital)

        # Update [user-pre-flop] and [total_chips] values.
        active_pot.user_post_flop = json.dumps(user_commited_chips)
        active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
        db.session.commit()

        return active_pot.user_post_flop


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

    if active_pot.ai_post_turn:
        ai_commited_chips = int(active_pot.ai_post_turn)
    else:
        ai_commited_chips = 0

    if active_pot.user_post_turn:
        user_commited_chips = int(active_pot.user_post_turn)
    else:
        user_commited_chips = 0

    ai_json_hole_cards = saved_hand.computer_opp_cards
    ai_hole_cards = []
    for card in json.loads(ai_json_hole_cards):
        ai_hole_cards.append(Card(card[1], card[0]))

    json_flop = saved_hand.flop
    flop = []
    for card in json.loads(json_flop):
        flop.append(Card(card[1], card[0]))

    json_turn = saved_hand.turn
    turn = []
    for card in json.loads(json_turn):
        turn.append(Card(card[1], card[0]))

    ai_post_turn_hand = ai_hole_cards + flop + turn
    ai_hand_rank = check_straight_flush(ai_post_turn_hand)

    if ai_hand_rank < 14 and ai_commited_chips == user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 90:
            active_pot.ai_post_turn = json.dumps(0)
            db.session.commit()

            return active_pot.ai_post_turn

        if rnum > 90:
            pot = int(active_pot.total_chips)

            ai_commited_chips += round(pot / 3)
            ai_stack -= round(pot / 3)
            pot += round(pot / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_turn

    elif ai_hand_rank < 14 and ai_commited_chips < user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 85:
            return json.dumps("xoxo")

        if rnum > 85 and rnum <= 95:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_turn

        if rnum > 95:
            if session["post_turn_raise_count"] <= 3:
                session["post_turn_raise_count"] += 1

            elif session["post_turn_raise_count"] > 3:
                rnum = random.randint(1, 100)
                if rnum <= 5:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_turn = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_turn
                else:
                    return json.dumps("xoxo")

            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            ai_commited_chips += round(updated_pot_val / 2)
            ai_stack -= round(updated_pot_val / 2)
            pot = updated_pot_val + round(updated_pot_val / 2)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_turn

    elif ai_hand_rank > 14 and ai_commited_chips == user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 65:
            session["post_turn_raise_count"] += 1

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += round(initial_pot_val / 3)
            ai_stack -= round(initial_pot_val / 3)
            pot = initial_pot_val + round(initial_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_turn

        elif rnum > 65:
            active_pot.ai_post_turn = json.dumps(0)
            db.session.commit()

            return active_pot.ai_post_turn

    elif ai_hand_rank > 14 and ai_commited_chips < user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 10:
            return json.dumps("xoxo")

        elif rnum > 10 and rnum <= 55:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_turn

        elif rnum > 55:
            if session["post_turn_raise_count"] <= 3:
                session["post_turn_raise_count"] += 1

            elif session["post_turn_raise_count"] > 3:
                rnum = random.randint(1, 100)
                if rnum <= 95:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_turn = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_turn
                else:
                    return json.dumps("xoxo")

            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            ai_commited_chips += round(updated_pot_val / 3)
            ai_stack -= round(updated_pot_val / 3)
            pot = updated_pot_val + round(updated_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_turn = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_turn


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

    if user_commited_chips < ai_commited_chips:

        difference = ai_commited_chips - user_commited_chips
        user_commited_chips += difference

        adjusted_user_capital = int(user.capital) - difference
        user.capital = json.dumps(adjusted_user_capital)

        active_pot.user_post_turn = json.dumps(user_commited_chips)
        active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
        db.session.commit()

        return active_pot.user_post_turn


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

    if active_pot.ai_post_river:
        ai_commited_chips = int(active_pot.ai_post_river)
    else:
        ai_commited_chips = 0

    if active_pot.user_post_river:
        user_commited_chips = int(active_pot.user_post_river)
    else:
        user_commited_chips = 0

    ai_json_hole_cards = saved_hand.computer_opp_cards
    ai_hole_cards = []
    for card in json.loads(ai_json_hole_cards):
        ai_hole_cards.append(Card(card[1], card[0]))

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

    ai_post_river_hand = ai_hole_cards + flop + turn + river
    ai_hand_rank = check_straight_flush(ai_post_river_hand)

    if ai_hand_rank < 14 and ai_commited_chips == user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 90:
            active_pot.ai_post_river = json.dumps(0)
            db.session.commit()

            return active_pot.ai_post_river

        if rnum > 90:
            pot = int(active_pot.total_chips)

            ai_commited_chips += round(pot / 3)
            ai_stack -= round(pot / 3)
            pot += round(pot / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_river

    elif ai_hand_rank < 14 and ai_commited_chips < user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 85:
            return json.dumps("xoxo")

        if rnum > 85 and rnum <= 95:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_river

        if rnum > 95:
            if session["post_river_raise_count"] <= 3:
                session["post_river_raise_count"] += 1

            elif session["post_river_raise_count"] > 3:
                rnum = random.randint(1, 100)
                if rnum <= 5:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_river = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_river
                else:
                    return json.dumps("xoxo")

            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            ai_commited_chips += round(updated_pot_val / 2)
            ai_stack -= round(updated_pot_val / 2)
            pot = updated_pot_val + round(updated_pot_val / 2)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_river

    elif ai_hand_rank > 14 and ai_commited_chips == user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 65:
            session["post_river_raise_count"] += 1

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += round(initial_pot_val / 3)
            ai_stack -= round(initial_pot_val / 3)
            pot = initial_pot_val + round(initial_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_river

        elif rnum > 65:
            active_pot.ai_post_river = json.dumps(0)
            db.session.commit()

            return active_pot.ai_post_river

    elif ai_hand_rank > 14 and ai_commited_chips < user_commited_chips:
        rnum = random.randint(1, 100)
        if rnum <= 10:
            return json.dumps("xoxo")

        elif rnum > 10 and rnum <= 55:
            difference = user_commited_chips - ai_commited_chips
            ai_commited_chips += difference

            initial_pot_val = int(active_pot.total_chips)

            ai_stack -= difference
            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(initial_pot_val + difference)
            db.session.commit()

            return active_pot.ai_post_river

        elif rnum > 55:
            if session["post_river_raise_count"] <= 3:
                session["post_river_raise_count"] += 1

            elif session["post_river_raise_count"] > 3:
                rnum = random.randint(1, 100)
                if rnum <= 95:
                    difference = user_commited_chips - ai_commited_chips
                    ai_commited_chips += difference

                    initial_pot_val = int(active_pot.total_chips)

                    ai_stack -= difference
                    session["ai_stack"] = ai_stack

                    active_pot.ai_post_river = json.dumps(ai_commited_chips)
                    active_pot.total_chips = json.dumps(initial_pot_val + difference)
                    db.session.commit()

                    return active_pot.ai_post_river
                else:
                    return json.dumps("xoxo")

            difference = user_commited_chips - ai_commited_chips

            initial_pot_val = int(active_pot.total_chips)

            ai_commited_chips += difference
            ai_stack -= difference

            updated_pot_val = initial_pot_val + difference

            ai_commited_chips += round(updated_pot_val / 3)
            ai_stack -= round(updated_pot_val / 3)
            pot = updated_pot_val + round(updated_pot_val / 3)

            session["ai_stack"] = ai_stack

            active_pot.ai_post_river = json.dumps(ai_commited_chips)
            active_pot.total_chips = json.dumps(pot)
            db.session.commit()

            return active_pot.ai_post_river


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

    if user_commited_chips < ai_commited_chips:

        difference = ai_commited_chips - user_commited_chips
        user_commited_chips += difference

        adjusted_user_capital = int(user.capital) - difference
        user.capital = json.dumps(adjusted_user_capital)

        active_pot.user_post_river = json.dumps(user_commited_chips)
        active_pot.total_chips = json.dumps(int(active_pot.total_chips) + difference)
        db.session.commit()

        return active_pot.user_post_river


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


@app.route("/texas_hold_em/win/<int:user_id>", methods=["GET", "POST"])
def won_hand(user_id):
    user = User.query.get_or_404(user_id)

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # The user has won this hand.
    int_pot = int(active_pot.total_chips)
    adjusted_user_capital = math.trunc(int(user.capital) + int_pot)
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
    adjusted_ai_stack = math.trunc(ai_stack + int_pot)
    session["ai_stack"] = adjusted_ai_stack

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [loss]")
    return redirect(f"/texas_hold_em/{user_id}")


@app.route("/texas_hold_em/draw/<int:user_id>", methods=["GET", "POST"])
def drew_hand(user_id):
    user = User.query.get_or_404(user_id)
    ai_stack = session["ai_stack"]

    saved_hand = TexasHoldEm.query.filter_by(user_id=user_id).first()
    active_pot = TexasHoldEmPot.query.filter_by(hand_id=saved_hand.id).first()

    # This hand ended in a draw, so the players split the pot 50:50.
    int_pot = int(active_pot.total_chips)
    adjusted_user_capital = math.trunc(int(user.capital) + int(int_pot / 2))
    user.capital = json.dumps(adjusted_user_capital)
    adjusted_ai_stack = ai_stack + (int_pot / 2)
    session["ai_stack"] = adjusted_ai_stack
    db.session.commit()

    saved_user_hands = TexasHoldEm.query.filter_by(user_id=user_id).all()
    for hand in saved_user_hands:
        db.session.delete(hand)

    db.session.commit()

    flash(f"Previous hand: [draw]")
    return redirect(f"/texas_hold_em/{user_id}")
