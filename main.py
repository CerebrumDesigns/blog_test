from flask import Flask, render_template, flash, request, redirect, url_for
from jinja2.utils import markupsafe
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, login_remembered, current_user
from webforms import UserForm, BlogForm, LoginForm, SearchForm, SimplifyForm
from flask_ckeditor import CKEditor
import openai

app = Flask(__name__)
ckeditor = CKEditor(app)
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

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    #author = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255), nullable=False)
    #Foreign Key to link to users (refer to primary key (id)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.now())
    #User can have many posts
    posts = db.relationship("Posts", backref="poster")

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

@app.route("/", methods=["POST", "GET"])
def home():
    form = SimplifyForm()
    if form.validate_on_submit():
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Summarize this for a second-grade student:\n\n {form.simplify_me.data}",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        form.simplify_me.data = ""
        simplified = (response["choices"][0]["text"])
        return render_template('index.html', simplified=simplified, form=form)
    else:
        print("02")
        return render_template('index.html', form=form)
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 3:
        return render_template('admin.html')
    else:
        flash("Sorry, this is only available to the Admin")
        return redirect("dashboard")


@app.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    form = BlogForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, slug=form.slug.data, poster_id=poster, content=form.content.data)
        # Clear the Form
        form.title.data = ""
        form.slug.data = ""
        #form.author.data = ""
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
       # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been Updated")
        return redirect(url_for("post", id=post.id))

    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("You are not authorised this post")
        posts = Posts.query.order_by(Posts.date_added)
        return render_template("posts.html",
                               posts=posts)

@app.route("/post/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    title = None
    id = current_user.id
    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post Deleted Successfully!")
            posts = Posts.query.order_by(Posts.id)
            return render_template("posts.html",
                                   title=title,
                                   posts=posts)
        except:
            flash("There was an issue, oops!")
            posts = Posts.query.order_by(Posts.id)
            return render_template("posts.html",
                                   title=title,
                                   posts=posts)
    else:
        flash("You are not authorised to delete this post")
        posts = Posts.query.order_by(Posts.id)
        return render_template("posts.html",
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
@login_required
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
@login_required
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

#pass staff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data

        posts = posts.filter(Posts.content.like("%" + post.searched + "%"))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html",
                               form=form,
                               searched=post.searched,
                               posts=posts)



if __name__ == '__main__':
    app.run(debug=True)
