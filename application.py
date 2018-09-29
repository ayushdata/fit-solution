import os
import time
from datetime import date
import requests
from flask import Flask, session, render_template, request, flash, redirect
from flask_session import Session
from tempfile import mkdtemp
from extras import apology, login_required, lookup, usd, Forex, collect
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure environment variable is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Ensures responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """ Homepage """
    session.clear()
    return render_template("index.html")

@app.route("/contactus")
def contactus():
    """ Contact us """
    return render_template("contactus.html")

@app.route("/forex", methods = ["GET", "POST"])
@login_required
def forex():
    """ Homepage of Foreign Exchange """
    if request.method == "POST":
        currency_from = request.form.get("currency_from")
        currency_to = request.form.get("currency_to")
        amount, currency_from_name, currency_to_name = Forex(currency_from, currency_to)
        outcome = f"1 {currency_from}({currency_from_name}) <<----->> {amount} {currency_to}({currency_to_name})"
        return render_template("forexshow.html", outcome = outcome)
    else:
        # Collecting names of all the currencies along with their symbols
        currency_list = collect()
        return render_template("forex.html", currency_list = currency_list)

@app.route("/stocktrade")
@login_required
def stocktrade():
    """ Homepage of Virtual Stock trading """
    return render_template("stocktrade.html")

@app.route("/stocktrade/quote", methods = ["GET", "POST"])
@login_required
def quote():
    """Quoting the price of the stock"""
    if request.method == "POST":

        # Perform a lookup of the stock's current price
        quote_dict = lookup(request.form.get("symbol"))
        # Pass data to the HTML file in case the price of the stock is found
        if quote_dict:
            return render_template("quoted.html", company=quote_dict["company"], price=quote_dict["price"], symbol=quote_dict["symbol"])
        else:
            return apology("No such stock found")
    else:
        return render_template("quote.html")

@app.route("/stocktrade/buy", methods = ["GET", "POST"])
@login_required
def buy():
    """Buying the shares"""
    if request.method == "POST":

        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        stock = lookup(symbol)
        # Ensures stock symbol was entered
        if not symbol:
            return apology("Please enter the stock symbol")
        # Ensures stock symbol is valid
        if not stock:
            return apology("Stock symbol does not exist")
        # Ensures user entered the valid number of shares
        if not shares or not shares.isdigit():
            return apology("Please enter valid number of shares")

        # Because int('0.5') return value error, we use int(float('0.5')
        if int(float(shares)) < 0:
            return apology("Please enter valid number of shares")
        price = stock["price"]
        try:
            cash = db.execute("SELECT cash from users WHERE id = :uid", {"uid": session["user_id"]}).fetchall()
        except:
            return apology("Couldn't connect to database")

        # If insufficient cash is present in the account
        if cash[0]['cash'] < price * int(shares):
            return apology("Sorry! You ran out of dollars")
        # Updating the balance possessed by the user
        try:
            db.execute("UPDATE users SET cash = cash - :cost WHERE id = :uid",
                       {"cost": price * int(shares), "uid": session["user_id"]})
            db.commit()
        except:
            return apology("Couldn't connect to database")
        # Reflecting the new purchase in the history table
        try:
            db.execute("INSERT INTO history (id, price, shares, date, symbol) VALUES (:uid, :priceShare, :numberOfShares, :dateOfPurchase, :stockSymbol)",
                       {"uid": session["user_id"], "priceShare": price, "numberOfShares": int(shares),
                       "dateOfPurchase": date.today(), "stockSymbol": symbol.upper()})
            db.commit()
        except:
            return apology("Couldn't connect to database")
        return redirect("/stocktrade/history")
    else:
        return render_template("buy.html")

@app.route("/stocktrade/sell", methods = ["GET", "POST"])
@login_required
def sell():
    """ Selling the shares """
    if request.method == "POST":

        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        price = lookup(symbol)["price"]
        # If user didn't input the symbol or the number of shares
        if not symbol:
            return apology("Symbol not entered")
        if not shares or not shares > 0:
            return apology("Number of shares not entered correctly")

        # Selecting the required stock symbol along with total number of stocks
        try:
            hist = db.execute("SELECT symbol, SUM(shares) AS shares from history WHERE id = :uid and symbol = :sym GROUP BY symbol", {"uid": session["user_id"], "sym": symbol}).fetchall()
        except:
            return apology("Couldn't connect to database")

        # If stock symbol is not possessed by the user
        if not hist:
            return apology("No such stock owned")
        # If lesser number of shares are owned by the user
        if hist[0]["shares"] < shares:
            return apology("You don't have enough shares to sell")

        # Update the cash possessed by the user in the users table
        try:
            db.execute("UPDATE users SET cash = cash + :cost WHERE id = :uid",
                            {"cost": price * shares, "uid":session["user_id"]})
            db.commit()
        except:
            return apology("Couldn't connect to database")
        # Insert the sale transaction in the history table
        try:
            db.execute("INSERT INTO history(id, price, shares, date, symbol) VALUES (:uid, :priceShare, :numberOfShares, :dateOfPurchase, :stockSymbol)",
                        {"uid": session["user_id"], "priceShare": price, "numberOfShares": -shares, "dateOfPurchase":date.today(), "stockSymbol": symbol})
            db.commit()
        except:
            return apology("Couldn't connect to database")

        # Redirect to the index page
        return redirect("/stocktrade/history")
    else:
        # try:
        stock = db.execute("SELECT DISTINCT symbol FROM history WHERE id = :uid GROUP BY symbol HAVING SUM(shares) > 0 ", {"uid": session["user_id"]}).fetchall()
        # except:
        #     return apology("Couldn't connect to database")
        return render_template("sell.html", stock=stock)

@app.route("/stocktrade/history")
@login_required
def history():
    """ History of transactions """
    try:
        hist = db.execute("SELECT price, shares, date, symbol FROM history WHERE history.id = :uid", {"uid": session["user_id"]}).fetchall()
    except:
        return apology("Couldn't connect to database")

    return render_template("history.html", hist=hist)


@app.route("/stocktrade/stocksHeld")
@login_required
def stocksHeld():
    """ Displays all the stocks currently in hand """
    if session["user_id"]:

        try:
            user = db.execute("SELECT cash FROM users WHERE id = :uid", {"uid":session["user_id"]}).fetchall()
        except:
            return apology("Couldn't connect to database")

        try:
            hist = db.execute("SELECT symbol, SUM(shares) AS shares FROM history WHERE id = :uid GROUP BY symbol",
                          {"uid": session["user_id"]}).fetchall()
        except:
            return apology("Couldn't connect to database")

        portfolio = {}
        grandTotal = 0.0

        try:
            for stock in hist:
                if stock["shares"] == 0:
                    continue
                time.sleep(2)
                jsonfile = requests.get("https://api.iextrading.com/1.0/stock/%s/quote" % stock["symbol"].lower()).json()
                price = jsonfile["close"]
                grandTotal += (stock["shares"] * price)
                portfolio[stock["symbol"].upper()] = [stock["shares"], price, stock["shares"] * price, jsonfile["companyName"]]
        except:
            return apology("NOT YOUR FAULT! !API malfunction!")

        return render_template("stocksHeld.html", cash=user[0]["cash"], portfolio=portfolio, grandTotal=grandTotal + user[0]["cash"])
    else:
        return url_for("login")

@app.route("/register", methods = ["GET", "POST"])
def register():
    """ Registration Page for new user """
    if request.method == "POST":
        password = request.form.get("password")
        if not request.form.get("name") or not request.form.get("email") or not password or not request.form.get("confirmation"):
            return apology("Incomplete data provided")
        if password != request.form.get("confirmation"):
            return apology("Passwords do not match")

        try:
            uid = db.execute("SELECT id from users WHERE email = :email", {"email": request.form.get("email")}).fetchall()
        except:
            return apology("Couldn't communicate to database")
        if uid:
            return apology("User already registered")
        try:
            db.execute("INSERT into users (name, email, hash) VALUES (:name, :email, :hashVal)",
                       {"name": request.form.get("name"), "email": request.form.get("email"),
                       "hashVal": generate_password_hash(request.form.get("password"))})
            db.commit()
        except:
            return apology("Couldn't communicate to database")

        try:
            uid = db.execute("SELECT id from users WHERE email = :email", {"email": request.form.get("email")}).fetchall()
        except:
            return apology("Couldn't communicate to database")
        session["user_id"] = uid[0]['id']
        return redirect("/stocktrade")

    else:
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    """ Login Page for existing users """
    # Forget any user_id
    session.clear()
    if request.method == "POST":

        if not request.form.get("email"):
            return apology("Email-id Missing", 403)
        if not request.form.get("password"):
            return apology("Password Missing", 403)
        try:
            rows = db.execute("SELECT * FROM users WHERE email = :email", {"email":request.form.get("email")}).fetchall()
            db.commit()
        except:
            return apology("Couldn't communicate to database")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/stocktrade")
    else:
        return render_template("login.html")

@app.route("/change_password", methods = ["GET", "POST"])
@login_required
def change_password():
    """ Registration Page for new user """
    if request.method == "POST":
        password = request.form.get("password")
        if not request.form.get("oldpassword") or not password or not request.form.get("confirmation"):
            return apology("Please input all the fields")
        old = db.execute("SELECT hash FROM users where id = :uid", {"uid": session["user_id"]}).fetchall()
        if not check_password_hash(old[0]["hash"], request.form.get("oldpassword")):
            return apology("Old Password is incorrect")

        if password != request.form.get("confirmation"):
            return apology("Passwords do not match, Please try again!", 404)
        hashVal = generate_password_hash(password)
        try:
            db.execute("UPDATE users SET hash = :hashVal where id = :uid", {"hashVal": hashVal, "uid": session["user_id"]})
            db.commit()
        except:
            return apology("Password Updation Failed")
        session.clear()
        return redirect("/")
    else:
        return render_template("change_password.html")

@app.route("/cryptos")
@login_required
def cryptos():
    """ Displays Bitcoins and Altcoins price """
    return render_template("cryptos.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
