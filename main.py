from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from flask_login import (
    UserMixin, login_user, logout_user,
    current_user, login_required, LoginManager
)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"



class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)



class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)],render_kw={"placeholder": "username"})
    email = StringField(validators=[InputRequired(), Length(min=5, max=80)],render_kw={"placeholder": "email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],render_kw={"placeholder": "password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already exists")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)],render_kw={"placeholder": "username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],render_kw={"placeholder": "password"})
    submit = SubmitField("Login")




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    cars = Car.query.all()
    return render_template("index.html", cars=cars)

@app.route("/search")
def search():
    brand = request.args.get("brand")
    year = request.args.get("year")
    price = request.args.get("price")

    query = Car.query

    if brand:
        query = query.filter(Car.brand == brand)
    if year:
        query = query.filter(Car.year == int(year))
    if price:
        price_min, price_max = map(int, price.split("-"))
        query = query.filter(Car.price.between(price_min, price_max))

    cars = query.all()
    return render_template("results.html", cars=cars)



@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for("index"))

    return render_template(
        "register.html",
        login_form=login_form,
        register_form=register_form
    )


@app.route("/register", methods=["POST"])
def register():
    register_form = RegistrationForm()

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            register_form.password.data
        ).decode("utf-8")

        user = User(
            username=register_form.username.data,
            email=register_form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()
        login_user(user)

        return redirect(url_for("index"))
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/account")
def account():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
