from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = \
"postgresql://zoomuser:strongpassword@localhost:5432/zoomauto"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Car(db.Model):
    __tablename__ = "car"   # 🔴 ОБОВʼЯЗКОВО

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)


@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)


@app.route("/search")
def search():
    brand = request.args.get("brand")
    year = int(request.args.get("year"))
    price_min, price_max = map(int, request.args.get("price").split("-"))

    cars = Car.query.filter(
        Car.brand == brand,
        Car.year == year,
        Car.price.between(price_min, price_max)
    ).all()

    return render_template("results.html", cars=cars)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        message = request.form.get("message")
        print("New support message:", message)
        return redirect(url_for("contact"))
    return render_template("contact.html")

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
    app.run(debug=True)
