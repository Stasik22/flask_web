from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.file import FileRequired
from tensorboard import default
from werkzeug.utils import secure_filename
from wtforms import SubmitField, FileField
from dotenv import load_dotenv
import os
import enum

from flask_login import (
    UserMixin, login_user, logout_user,
    current_user, login_required, LoginManager
)

from flask_wtf import FlaskForm, file
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


class GenderEnum(enum.Enum):
    Male = "Male"
    Female = "Female"


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
    image = db.Column(db.String(200), nullable=False, default="static/users_icon_upload/account_icon.png")
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(GenderEnum, name="gender_type"),nullable=False)
    contacts = db.Column(db.String(25), unique=True)


    def validation_username_email(self, username, email):
        self.username = username
        self.email = email

        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already exists")
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already exists")




class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)],render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Length(min=5, max=80)],render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already exists")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],render_kw={"placeholder": "Password"})
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
    return render_template("search.html", cars=cars)

@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            print("LOGGED:", user.username)
            return redirect(url_for("index"))

    return render_template(
        "register.html",
        login_form=login_form,
        register_form=register_form
    )

@app.route("/register", methods=["GET", "POST"])
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

app.config['UPLOAD_FOLDER'] = 'static/images/users_icon_upload'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class FileUploadForm(FlaskForm):
    file = FileField("File", validators=[FileRequired()])
    submit = SubmitField("Upload")

@app.route("/dashboard/photo_edit",  methods=["GET", "POST"])
@login_required
def photo_edit():
    form = FileUploadForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        current_user.image = filename
        db.session.commit()
        return redirect(url_for("update_account"))
    return render_template("photo_edit.html", form=form)


@app.route("/dashboard/account", methods=["GET", "POST"])
@login_required
def update_account():
    if request.method == "POST":
        current_user.username = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.address = request.form.get("address")
        current_user.city = request.form.get("city")
        current_user.date_of_birth = request.form.get("birth_date")
        current_user.gender = request.form.get("gender")
        current_user.contacts = request.form.get("contact_number")
        current_user.email = request.form.get("account_email")

        password = request.form.get("account_password")
        if password:
            current_user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        if current_user.date_of_birth == "":
            current_user.date_of_birth = None

        db.session.commit()
        return redirect(url_for("update_account"))

    return render_template("account.html")

@app.route("/dashboard/favorites", methods=["GET", "POST"])
@login_required
def dashboard_favorites():
    return render_template("favorites.html")

@app.route("/dashboard/helpdesk", methods=["GET", "POST"])
@login_required
def dashboard_helpdesk():
    return render_template("helpdesk.html")

@app.route("/dashboard/saved", methods=["GET", "POST"])
@login_required
def dashboard_saved():
    return render_template("saved.html")

@app.route("/dashboard/settings", methods=["GET", "POST"])
@login_required
def dashboard_settings():
    return render_template("settings.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/offers/<int:car_id>")
def offer(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template("offers.html", car=car)


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/account", methods=["GET", "POST"])
def account():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
