# Import Python's [os] module, which provides functions for interacting w/ the operating system.
import os

# Import Flask itself, from [flask], and import all of the Flask features...
# (i.e., render_template, request) that you will be using in this application.
from flask import Flask, request, render_template, redirect, flash, session, g

# Import SQLAlchemy (db), the [connect_db] function, and the classes you've created from the [models.py] file.
from models import bcrypt, db, connect_db, User

# Import the forms you've created from the [forms.py] file.
from forms import UserLoginForm, CreateAccountForm

from game_elements import Player, Card, Deck

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

            # Note to self: Tighten-up password form validators... DO NOT manipulate password data w/out user knowledge!!
            if k == "password":
                data[k] = data[k].replace(" ", "")
            if k != "csrf_token" and k != "password":
                data[k] = data[k].lower()
                data[k] = data[k].replace(" ", "")

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
            username = existing_user.username

            # If a user logs in successfully, store their username in...
            # session storage to keep track of which specific user is logged in.
            session["username"] = username

            return redirect(f"/user/{username}")

    return render_template("base.html", form=form)


@app.route("/create_account", methods=["GET", "POST"])
def register():
    """Direct new users to the account registration form."""

    form = CreateAccountForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        ### Note to self: replace this "data" dictionary w/ specific requests --> username, password, email address...
        ### Note to self: research non-strict way to complete this step.

        for k in data:
            if k == "password":
                data[k] = data[k].replace(" ", "")
            if k != "csrf_token" and k != "password":
                data[k] = data[k].lower()
                data[k] = data[k].replace(" ", "")

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
                return redirect("/new_user")

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


@app.route("/user/<username>", methods=["GET", "POST"])
def successful_login(username):
    user = User.query.get_or_404(username)

    # If a user attempts to access another user's profile...
    # restart the application (+) flash a helpful message.
    if session["username"] != username:
        flash("Access denied.")
        return redirect("/")

    return render_template("successful_login.html", user=user)


@app.route("/texas_hold_em/<username>", methods=["GET", "POST"])
def play_texas_hold_em(username):
    user = User.query.get_or_404(username)

    # If a user attempts to access another user's profile...
    # restart the application (+) flash a helpful message.
    if session["username"] != username:
        flash("Access denied.")
        return redirect("/user/<username>")

    # Establish a [players] variable and set it equal to...
    # an empty list. Use it to store each instance of the...
    # Player class that you create for a given game.
    players = []

    # Create an [active_user] instance of the Player class...
    # This is (obviously) the user who is logged-in + actively playing.
    active_user = Player(username, 100)
    players.append(active_user)

    # Create a [computer_opponent] instance of the Player class...
    # This poker-bot is named "Cortana" after the fictional AI in Halo.
    computer_opponent = Player("Cortana", 100)
    players.append(computer_opponent)

    # Create an instance of the Deck class, build it, and shuffle it.
    new_deck = Deck()
    new_deck.shuffle()

    for card in new_deck.cards:
        print(card.reveal())

    for i in range(1, 3):
        for player in players:
            player.accept_dealt_card(new_deck)

    flop = new_deck.flop_protocol()
    ### Add [flop] to session storage --> *this is not necessarily a good idea.
    ### session["flop"] = flop
    for card in flop:
        print(f"flop: {card.reveal()}")

    turn = new_deck.turn_protocol()
    print(f"turn: {turn[0].reveal()}")

    river = new_deck.river_protocol()
    print(f"river: {river[0].reveal()}")

    return render_template(
        "texas_hold_em.html",
        user=user,
        players=players,
        flop=flop,
        turn=turn,
        river=river,
    )


@app.route("/delete/user/<username>", methods=["POST"])
def destroy(username):
    user = User.query.get_or_404(username)

    db.session.delete(user)
    db.session.commit()

    return redirect("/")
