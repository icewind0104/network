from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, IntegerField, TextAreaField, HiddenField, SelectField, validators
from wtforms.validators import DataRequired
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect

class NeedSearchIdField(StringField):
    def __init__(self, *args, related_model, related_column, **kwargs):
        self.related_model = related_model
        self.related_column = related_column
        StringField.__init__(self, *args, **kwargs)

class BooleanSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        SelectField.__init__(self, *args, **kwargs)

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
    addr = StringField('addr')
    user = StringField('user', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    mac = StringField('mac', render_kw={'autocomplete': 'off'})
    device = TextAreaField('device', render_kw={'autocomplet': 'off', 'cols':'40', 'rows':'2'})
    net = StringField('net')
    sync = BooleanField('sync', default="sync")

class Login(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={'class': 'uk-width-1-1 uk-form-large', 'placeholder': '登录名', 'autocomplete': 'off'})
    password = PasswordField('password', validators=[DataRequired()], render_kw={'class': 'uk-width-1-1 uk-form-large', 'placeholder': '密码', 'autocomplete': 'off'})
    remember = BooleanField('remember', default='y')

#class Asset(RedirectForm):
#    id = IntegerField('id', render_kw={'class':'uk-hidden'})
#    serial= StringField('serial', render_kw={'autocomplete': 'off'})
#    catagory = SelectField('catagory', choices=[('台式主机', '台式主机'), ('显示器', '显示器'), ('笔记本电脑', '笔记本电脑'), ('其他', '其他')])
#    name = StringField('name', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
#    employee_id = NeedSearchIdField('employee_id', related_model='employees', related_column='name', render_kw={'autocomplete': 'off'})
#    note = StringField('note', render_kw={'autocomplete': 'off'})

class Employee(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    name = StringField('name', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    department_id = SelectField('department_id')
    status = BooleanSelectField('status', choices=[('1', '在职'), ('0', '离职')])

class Department(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    name = StringField('name', validators=[DataRequired()], render_kw={'autocomplete': 'off'})
    ipstart = StringField('ipstart', render_kw={'autocomplete': 'off'})
    ipend = StringField('ipend', render_kw={'autocomplete': 'off'})
    parent = StringField('parent', render_kw={'autocomplete': 'off', 'class':'uk-hidden'})
    
class Host(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    cpu = StringField('cpu', render_kw={'autocomplete': 'off'})
    memory = StringField('memory', render_kw={'autocomplete': 'off'})
    motherboard = StringField('motherboard', render_kw={'autocomplete': 'off'})
    graphics = StringField('graphics', render_kw={'autocomplete': 'off'})
    note = StringField('note', render_kw={'autocomplete': 'off'})
    asset_sn = StringField('asset_sn', render_kw={'autocomplete': 'off'})
    employee_id = NeedSearchIdField('employee_id', related_model='employees', related_column='name', render_kw={'autocomplete': 'off'})
    
class Display(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    vendor = StringField('vendor', render_kw={'autocomplete': 'off'})
    model = StringField('model', render_kw={'autocomplete': 'off'})
    serial = StringField('serial', render_kw={'autocomplete': 'off'})
    note = StringField('note', render_kw={'autocomplete': 'off'})
    asset_sn = StringField('asset_sn', render_kw={'autocomplete': 'off'})
    employee_id = NeedSearchIdField('employee_id', related_model='employees', related_column='name', render_kw={'autocomplete': 'off'})
    
class Laptop(RedirectForm):
    id = IntegerField('id', render_kw={'class':'uk-hidden'})
    vendor = StringField('vendor', render_kw={'autocomplete': 'off'})
    model = StringField('model', render_kw={'autocomplete': 'off'})
    serial = StringField('serial', render_kw={'autocomplete': 'off'})
    note = StringField('note', render_kw={'autocomplete': 'off'})
    asset_sn = StringField('asset_sn', render_kw={'autocomplete': 'off'})
    employee_id = NeedSearchIdField('employee_id', related_model='employees', related_column='name', render_kw={'autocomplete': 'off'})
    