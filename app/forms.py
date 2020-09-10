from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length, NumberRange
from app.models import Users

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+.])[\w\d~`!@#$%^&*()-_=+{[|}:;'?/>.<\"\]\\,]{6,}")])
  password2 = PasswordField(
    'Confirmation', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = Users.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = Users.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')

class PasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(), Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+.])[\w\d~`!@#$%^&*()-_=+{[|}:;'?/>.<\"\]\\,]{6,}")])
  password2 = PasswordField(
    'Confirmation', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Change Password')

class EmailForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  email2 = StringField('Email', validators=[DataRequired(), EqualTo('email')])
  submit = SubmitField('Change Email')

class WatchForm(FlaskForm):
  symbol = StringField('Symbol', validators=[DataRequired(), Length(min=1, max=5, message="Invalid Symbol")])
  submitAdd = SubmitField('Add to Watchlist')

class BuyForm(FlaskForm):
  symbol = StringField('Symbol', validators=[DataRequired(), Length(min=1, max=5)])
  share = IntegerField('Share', validators=[DataRequired()])
  submitBuy = SubmitField('Buy')

class SellForm(FlaskForm):
  symbol = StringField('Symbol', validators=[DataRequired(), Length(min=1, max=5)])
  share = IntegerField('Share', validators=[DataRequired(), NumberRange(min=1, message="Share Minimum=1")])
  submit = SubmitField('Sell')

class ResetPasswordRequestForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')