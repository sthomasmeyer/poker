# Import [FlaskForm], a Flask-specific subclass of WTForms [Form] base class.
from flask_wtf import FlaskForm

# Import desired basic fields (i.e., BooleanField, IntegerField) from [wtforms].
# These generally represent scalar data types w/ single values, and...
# refer to a single input from the form. For example, there is a [DecimalField()]...
# w/ parameters related to # of places, rounding (up or down), and number format.
from wtforms import StringField, EmailField, PasswordField, IntegerField

# Import desired validators (i.e., URL, InputRequired) from [wtforms.validators].
# Validators in WTForms are designd to ensure a given input fulfills some criterion...
# For example, there is a [Regexp()] validator that compares the value of the field...
# against a user-provided regexp.
from wtforms.validators import InputRequired, Email, Length, Regexp


class TexasHoldEmBet(FlaskForm):
    bet = IntegerField("Bet")


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=24)])
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=24)]
    )


class CreateAccountForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(max=24),
            Regexp("^[\S]+$", message="Your username must not contain spaces."),
        ],
    )
    email = EmailField(
        "Email",
        validators=[
            InputRequired(),
            Email(check_deliverability=True),
            Length(min=3, max=254),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=8, max=24),
            Regexp("^[\S]+$", message="Your password must not contain spaces."),
            Regexp(
                ".*[a-z].*",
                message="Your password must contain at least one lower-case character.",
            ),
            Regexp(
                ".*[A-Z].*",
                message="Your password must contain at least one upper-case character.",
            ),
            Regexp(
                ".*\d.*",
                message="Your password must contain at least one number (0-9).",
            ),
        ],
    )
