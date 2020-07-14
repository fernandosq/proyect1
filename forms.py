from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField,RadioField,SelectField,DateField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrar')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    options=RadioField('options', choices=[("ISBN"), ("TITLE"), ("AUTHOR")])
    buscador = StringField("")
    search_result = SubmitField('search_result')

class ReviewsForm(FlaskForm):
    review_tex  =StringField('review_tex',validators=[ DataRequired(),Length(max=200)])
    review_score = SelectField("review_score",choices=[1, 2, 3, 4, 5],validators=[DataRequired()])
    submit = SubmitField('post review')
