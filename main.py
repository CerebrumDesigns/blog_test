from flask import Flask, render_template
from jinja2.utils import markupsafe
from markupsafe import Markup
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
import jinja2

# markupsafe.Markup()
# Markup('')

class LoginForm(FlaskForm):
        email = StringField(label='Email')
        password = PasswordField(label='Password')


app = Flask(__name__)
app.secret_key = "1234"

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    return render_template('login.html', form=login_form)

@app.route("/blog")
def blog():
    return render_template('blog.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.route("/denied")
def denied():
    return render_template("denied.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == '__main__':
    app.run(debug=True)