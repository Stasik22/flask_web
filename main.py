from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(host = "", debug = True)