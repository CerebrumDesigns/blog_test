from flask import Flask, render_template, flash, request, redirect, url_for
from jinja2.utils import markupsafe
from markupsafe import Markup
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, email_validator, Length, EqualTo
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, login_remembered, current_user

app = Flask(__name__)
app.secret_key = "1234"
app.config["SECRET_KEY"] = "my test key"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///add_user.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Horeca1986@localhost/users"
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.now())


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255), nullable=False)

    # HASHING PASSWORDS>>>
    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"AddUser {self.name}"


db.create_all()


class UserForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired("You need to complete this field")])
    username = StringField(label='Username', validators=[DataRequired("You need to provide a username")])
    email = EmailField(label='Email', validators=[Email("Please enter a valid email address")])
    fav_color = StringField(label='Favorite Color')
    password_hash = PasswordField(label='Password', validators=[DataRequired("You need to provide a Password"),
                                                                EqualTo("password_hash2",
                                                                        message="The passwords must match!")])
    password_hash2 = PasswordField(label='Password', validators=[DataRequired("Please confirm your Password"),
                                                                 EqualTo("password_hash",
                                                                         message="Your passwords must match")])
    submit = SubmitField(label="Submit")


class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired("Please enter a valid username")])
    password = PasswordField(label='Password')
    submit = SubmitField(label="Log in")


class BlogForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired("You need to complete this field")])
    content = StringField(label="Content", validators=[DataRequired("You need to complete this field")],
                          widget=TextArea())
    author = StringField(label="Author", validators=[DataRequired("You need to complete this field")])
    slug = StringField(label="Slug", validators=[DataRequired("You need to complete this field")])
    submit = SubmitField(label="Submit")


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    form = BlogForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, slug=form.slug.data, author=form.author.data, content=form.content.data)
        # Clear the Form
        form.title.data = ""
        form.slug.data = ""
        form.author.data = ""
        form.content.data = ""

        # Add post to database
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully!")

    blog_posts = Posts.query.order_by(Posts.id)

    # Redirect to Webpage
    return render_template("add_post.html",
                           form=form,
                           posts=blog_posts)


@app.route("/posts")
def posts():
    posts = Posts.query.order_by(Posts.date_added)
    return render_template("posts.html",
                           posts=posts)


@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = BlogForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been Updated")
        return redirect(url_for("post", id=post.id))

    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


@app.route("/post/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    title = None
    form = BlogForm()

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post Deleted Successfully!")
        posts = Posts.query.order_by(Posts.id)
        return render_template("posts.html",
                               form=form,
                               title=title,
                               posts=posts)
    except:
        flash("There was an issue, oops!")
        posts = Posts.query.order_by(Posts.id)
        return render_template("posts.html",
                               form=form,
                               title=title,
                               posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!  Thanks For Stopping By...")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.username = request.form["username"]
        name_to_update.email = request.form["email"]
        name_to_update.fav_color = request.form["fav_color"]
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Oops, that did not work")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)
    return render_template("dashboard.html")


@app.route("/blog")
def blog():
    return render_template('blog.html')


@app.route("/date")
def date():
    return


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


@app.route("/user/add", methods=["POST", "GET"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hash_pw = generate_password_hash(password=form.password_hash.data)
            user = Users(name=form.name.data, email=form.email.data, fav_color=form.fav_color.data,
                         password_hash=hash_pw, username=form.username.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.fav_color.data = ""
        form.password_hash.data = ""
        flash("User added Successfully")
    our_users = Users.query.order_by(Users.id)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.username = request.form["username"]
        name_to_update.email = request.form["email"]
        name_to_update.fav_color = request.form["fav_color"]
        try:
            db.session.commit()
            flash("User updated successfully")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Oops, that did not work")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route("/delete/<int:id>")
def delete(id):
    name_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(name_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        our_users = Users.query.order_by(Users.id)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    except:
        flash("There was an issue, oops!")
        our_users = Users.query.order_by(Users.id)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)


if __name__ == '__main__':
    app.run(debug=True)
