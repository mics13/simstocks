from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, PasswordForm, EmailForm, WatchForm, BuyForm, SellForm, ResetPasswordRequestForm, ResetPasswordForm
from app.helper import usd, lookup
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Watch, History
from werkzeug.urls import url_parse
from app.email import send_password_reset_email
import decimal
from sqlalchemy.sql import func

app.jinja_env.filters["usd"] = usd

@app.route("/")
@app.route('/index')
def index():
  # home page with brief introdcution to the site
  return render_template("index.html")

'''User Control'''
@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = Users(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Thank you for registering with SimStocks!')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = Users.query.filter_by(username=form.username.data).first_or_404()
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    # the next query string argument is set to the original URL, so the application can use that to redirect back after login.
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc !='':
      next_page = url_for('index')
    flash(f'Welcome Back, {current_user.username}!')
    return redirect(url_for('index'))
  return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route("/account")
@login_required
def account():
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  return render_template("account.html", username=current_user.username, cash=current_user.cash, email=current_user.email, user=user)

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
  form = PasswordForm()
  if form.validate_on_submit():
    # Insert into database new password
    user = Users.query.filter_by(username=current_user.username).first_or_404()
    user.set_password(form.password.data)
    db.session.commit()
    flash('Your password has been changed')
    return redirect(url_for('account'))
  return render_template('password.html', title='Password', form=form)


@app.route("/email", methods=["GET", "POST"])
@login_required
def email():
  form = EmailForm()
  if form.validate_on_submit():
    # Insert into database new password
    user = Users.query.filter_by(username=current_user.username).first_or_404()
    user.email = form.email.data
    db.session.commit()
    flash('Your Email has been changed')
    return redirect(url_for('email'))
  return render_template('email.html', title='Email', form=form)

@app.route("/watchlist")
@login_required
def watchlist():
  watchForm = WatchForm()
  buyForm = BuyForm()
  # load user info
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  # for page rendering
  watch_lst = []
  watches = Watch.query.filter_by(user=user).all()
  for watch in watches:
    quote = lookup(watch.symbol)
    watch_lst.append((quote["symbol"], quote["name"], quote["price"]))
  return render_template("watchlist.html", watch_lst=watch_lst, title='Watchlist', watchForm=watchForm, buyForm=buyForm)
  
  
@app.route("/add", methods=["POST"])
def add():
  watchForm = WatchForm()
  # load user info
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  if watchForm.validate_on_submit():
    quote = lookup(watchForm.symbol.data)
    if quote == None:
      flash("No Data")
      return redirect(url_for("watchlist"))
    # check if symbol in watchlist, if not in watchlist, add to watchlist
    try:
      # try will fail if Watch.query.filter_by(user=user).filter_by(symbol=quote['symbol']).first == None
      # print('attempt1---------')
      Watch.query.filter_by(user=user).filter_by(symbol=quote["symbol"]).first().symbol
      flash("Symbol already in watchlist")
      return redirect(url_for("watchlist"))
    except:
      watch = Watch(user=user, symbol=quote["symbol"])
      db.session.add(watch)
      db.session.commit()
      flash("Symbol added to watchlist")
      return redirect(url_for("watchlist"))
  flash("Invalid Input")
  return redirect(url_for("watchlist"))  
  # elif watchForm.submitAdd.data and not watchForm.validate():
  #   flash("Invalid Symbol")
  #   return redirect(url_for('watchlist'))

@app.route("/buy", methods=["POST"])
def buy(): 
  buyForm = BuyForm()
  # load user info
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  if buyForm.validate_on_submit():
    # lookup for price
    quote = lookup(buyForm.symbol.data)
    if quote == None:
      flash("No Data")
      return redirect(url_for('watchlist'))
    # query how much cash the user currently has
    balance = user.cash
    if balance < (buyForm.share.data * quote["price"]):
      flash(f"Can't Afford! Your current balance is ${round(balance, 2)}.")
      return redirect(url_for('watchlist'))
      # if can afford, put transaction into record
      # history table: id, users_id, symbol, name, price, shares, time
    tran = History(user=user, symbol=quote["symbol"], name=quote["name"], price=quote["price"], share=buyForm.share.data)
    db.session.add(tran)
    # update user cash balance
    # balance is of decimal.decimal class
    user.cash = (balance - decimal.Decimal(buyForm.share.data * quote["price"]))
    db.session.commit()
    flash("{} successfully purchased {} shares of {} at ${}".format(user.username, buyForm.share.data, quote["symbol"], quote["price"]))
    return redirect(url_for("watchlist"))
  flash("Invalid Input")
  return redirect(url_for("watchlist")) 
  
@app.route("/portfolio")
@login_required
def portfolio():
  sellForm = SellForm()
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  # render user's portfolio
  # check users cash balance
  balance = user.cash
  # fetch all stocks owned and get current price
  port = db.session.query(History.symbol, History.name, func.sum(History.share).label("shares")).filter_by(user=user).group_by(History.symbol, History.name).having(func.sum(History.share)>0)    
  # if the user is not holding any stock, we only show the cash he holds, and of course his account total = cash
  if port.count()== 0:
    return render_template("portfolio.html", rows=[], cash=balance, total=balance)
  # create a new list for table rendering
  # convert the tuples in records into list and append current price and current stock worth
  rows = []
  shareWorth = 0
  for row in port:
    # symbol, name, share, price, total
    # row[2] is sum(share), can't use row.sum(share) for syntax reason
    r = [row.symbol, row.name, row.shares]
    current_price = lookup(row.symbol)["price"]     
    r.extend([current_price, row.shares * current_price])
    rows.append(r)
    shareWorth += row.shares * current_price
  # user's cash + current stock worth
  total = balance + decimal.Decimal(shareWorth)
  return render_template("portfolio.html", rows=rows, cash=balance, total=total, sellForm=sellForm)

@app.route("/sell", methods=["POST"])
def sell(): 
  sellForm = SellForm()
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  if sellForm.validate_on_submit():
    # fetch number of symbols owned, return tuple
    shareOwned = db.session.query(func.sum(History.share).label("shares")).filter_by(user=user, symbol=sellForm.symbol.data).first() 
    # shareOwned = db.session.execute("SELECT SUM(share) FROM history WHERE user_id = (SELECT id FROM Users WHERE username = :name) AND symbol = :symbol", {"name": session["user_id"], "symbol": symbol_sell}).first()
    if shareOwned[0] == None or shareOwned[0] < sellForm.share.data:
      quote = lookup(sellForm.symbol.data)
      if quote == None:
        flash("No Data")
        return redirect(url_for("portfolio"))
      flash("You don't have enough share.")    
      return redirect(url_for("portfolio"))
    else:
      # fetch price
      quote = lookup(sellForm.symbol.data)
      # query how much cash the user currently has 
      balance = user.cash
      # update user cash balance
      user.cash = balance + decimal.Decimal(sellForm.share.data * quote["price"])
      # insert new transction history
      tran = History(user=user, symbol=quote["symbol"], name=quote["name"], price=quote["price"], share=-sellForm.share.data)
      db.session.add(tran)
      db.session.commit()
      flash("{} successfully sold {} shares of {} at ${}".format(user.username, sellForm.share.data, quote["symbol"], quote["price"]))
      return redirect(url_for('.portfolio'))
  return render_template('portfolio.html', title='Sign In', sellForm=sellForm)

@app.route("/history")
@login_required
def history():
  """Show history of transactions"""
  user = Users.query.filter_by(username=current_user.username).first_or_404()
  h = History.query.filter_by(user=user).all()
  return render_template("history.html", rows=h)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = ResetPasswordRequestForm()
  if form.validate_on_submit():
    user = Users.query.filter_by(email=form.email.data).first()
    if user:
      send_password_reset_email(user)
    flash('Check your email for the instructions to reset your password')
    return redirect(url_for('login'))
  return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  user = Users.verify_reset_password_token(token)
  if not user:
    return redirect(url_for('index'))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    user.set_password(form.password.data)
    db.session.commit()
    flash('Your password has been reset.')
    return redirect(url_for('login'))
  return render_template('reset_password.html', form=form)