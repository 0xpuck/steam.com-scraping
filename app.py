import requests

from flask import Flask, request, render_template

from helpers import Database
import requests

STEAM_SESSION = "cafea932c9929bccba6f1583"

app = Flask(__name__)
db = Database().get_instance()

@app.route("/")
def index():
    minprice = request.args.get("minprice", 30)
    maxprice = request.args.get("maxprice", 2000)
    auto_refresh = request.args.get("auto_refresh", "off") != "on"
    minprice = int(minprice)
    maxprice = int(maxprice)
    limit = request.args.get("limit", 50)
    limit = int(limit)

    return render_template(
        "index.html",
        listings=db.get_listings(minprice, maxprice, limit),
        minprice=minprice,
        maxprice=maxprice,
        limit=limit,
        auto_refresh=auto_refresh
    )

if __name__ == "__main__":
    app.run()