from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


cars = [
    {"brand": "bmw", "year": 2023, "price": 18000, "name": "BMW X3"},
    {"brand": "audi", "year": 2022, "price": 15000, "name": "Audi A4"},
    {"brand": "mercedes", "year": 2024, "price": 35000, "name": "Mercedes C"},
]
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        message = request.form.get("message" , "message1")
        print("New support message:", message)
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/search")
def search():
    brand = request.args.get("brand")
    year = int(request.args.get("year"))
    price_min, price_max = map(int, request.args.get("price").split("-"))

    filtered = [
        car for car in cars
        if car["brand"] == brand
        and car["year"] == year
        and price_min <= car["price"] <= price_max
    ]
    return render_template("results.html", cars=filtered)

@app.route("/account")
def account():
    return render_template("account.html")
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(host = "", debug = True)