from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def about():
    return render_template("contact.html")

@app.route("/account")
def account():
    return render_template("account.html")

if __name__ == '__main__':
    app.run(host = "", debug = True)