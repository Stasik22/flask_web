from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Car(db.Model, UserMixin):
    __tablename__ = "car"
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),unique = True, nullable=False)
    email = db.Column(db.String(120),unique = True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "username"})
    email = StringField(validators=[InputRequired(), Length(min=20, max=80)], render_kw={"placeholder": "email"})
    password = PasswordField(validators=[InputRequired(), Length(min = 8, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Register")

    def username_validate(self, username):
        existing_user = User.query.filter_by(username=username.data).first()

        if existing_user:
            raise ValidationError("Username already exists, please choose another one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "username"})
    password = PasswordField(validators=[InputRequired(), Length(min = 8, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Login")

    def check_username_valid(self, username, password):
        user = User.query.filter_by(username=username.data).first()

        if user and check_password_hash(user.password, password):
            return index
        else:
            raise ValidationError("Incorrect username or password.")


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


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(username=form.username.data, email=form.email.data,  password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/login" , methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("account"))




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



if __name__ == "__main__":
    app.run(debug=True)
