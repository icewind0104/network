from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, IntegerField, TextAreaField, HiddenField
from wtforms.validators import DataRequired
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect

class RedirectForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def redirect(self, endpoint='index', **values):
        return redirect(request.referrer or url_for(endpoint, **values))

class Net(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    name = StringField('name', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    ipstart = StringField('ipstart', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    ipend = StringField('ipend', validators=[DataRequired()], render_kw={'autocomplete': 'off'})

class Ip(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    addr = StringField('addr', render_kw={'class':'uk-hidden'})
    user = StringField('user', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    mac = StringField('mac', render_kw={'autocomplete': 'off'})
    device = TextAreaField('device', render_kw={'autocomplet': 'off', 'cols':'40', 'rows':'2'})
    net = IntegerField('net', render_kw={'class':'uk-hidden'})

class Login(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={'class': 'uk-width-1-1 uk-form-large', 'placeholder': '登录名', 'autocomplete': 'off'})
    password = PasswordField('password', validators=[DataRequired()], render_kw={'class': 'uk-width-1-1 uk-form-large', 'placeholder': '密码', 'autocomplete': 'off'})
