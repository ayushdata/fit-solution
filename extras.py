import os
import csv
import json
import requests
import urllib.request
from functools import wraps
from alpha_vantage.timeseries import TimeSeries
from flask import redirect, render_template, request, session

# Fetches the real-time price of selected stock from AlphaVantage's API
def Forex(currency_from, currency_to):
    datastore = json.loads(json.dumps(requests.get(f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency_from}&to_currency={currency_to}&apikey={os.getenv('API_KEY')}").json()))
    return datastore["Realtime Currency Exchange Rate"]['5. Exchange Rate'], datastore["Realtime Currency Exchange Rate"]['2. From_Currency Name'], datastore["Realtime Currency Exchange Rate"]['4. To_Currency Name']

# Collects names of different currencies from Open Exchange API
def collect():
    datastore = json.loads(json.dumps(requests.get("https://openexchangerates.org/api/currencies.json").json()))
    return datastore

# Format the currency in USD
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Decorator function to verify if the user is logged in or requires a login to complete the request
def login_required(f):
    """ Decorate routes to require login. """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def lookup(symbol):
    """Look up quote for symbol."""

    # Reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # Reject symbol if it contains comma
    if "," in symbol:
        return None

    try:
        # Fetch the price
        jsonfile = requests.get("https://api.iextrading.com/1.0/stock/%s/quote" % symbol.lower()).json()
        # Return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "price": jsonfile["close"],
            "company": jsonfile["companyName"],
            "symbol": symbol.upper()
        }

    except:
        return None
