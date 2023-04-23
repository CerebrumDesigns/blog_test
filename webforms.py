from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, email_validator, Length, EqualTo
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

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
    #content = StringField(label="Content", validators=[DataRequired("You need to complete this field")],
                         # widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired("You need to complete this field")])
    author = StringField(label="Author")
    slug = StringField(label="Slug", validators=[DataRequired("You need to complete this field")])
    submit = SubmitField(label="Submit")

class SearchForm(FlaskForm):
    searched = StringField(label='Search')
    submit = SubmitField(label="Search")

class SimplifyForm(FlaskForm):
    simplify_me = StringField(validators=[DataRequired("You need to complete this field")], widget=TextArea())
    submit = SubmitField(label="Simplify")
