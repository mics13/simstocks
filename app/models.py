from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import app

class Users(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  email = db.Column(db.String(120), index=True, unique=True)
  cash = db.Column(db.Numeric(), nullable=False, default=10000)
  transactions = db.relationship("History", backref="user")
  watch = db.relationship("Watch", backref="user")

  def __repr__(self):
    return f'<User {self.username}>'
  
  def set_password(self, password):
    self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def avatar(self, size):
    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

  def get_reset_password_token(self, expires_in=600):
    return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

  @staticmethod
  def verify_reset_password_token(token):
    try:
      id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    except:
      return
    return Users.query.get(id)

class History(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(6), nullable=False)
  name = db.Column(db.String(200), nullable=False)
  price = db.Column(db.Numeric(), nullable=False)
  share = db.Column(db.Integer, nullable=False)
  time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

  def __repr__(self):
    return f'<symbol {self.symbol}, price {self.price}, share {self.share}>'

class Watch(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  symbol = db.Column(db.String(6), nullable=False)
  
  def __repr__(self):
    return f'<watch {self.symbol}>'

@login.user_loader
def load_user(id):
  return Users.query.get(int(id))

