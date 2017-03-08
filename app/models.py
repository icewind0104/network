from app import db, mylib

class employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    department = db.Column(db.String(64), nullable=False)
    assets = db.relationship('assets', backref='assets_user', lazy='dynamic')

class nets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    ipstart = db.Column(db.Integer, nullable=False)
    ipend = db.Column(db.Integer, nullable=False)
    ips = db.relationship('ips', backref='owner', lazy='dynamic')
    @property
    def ipstart_str(self):
        return mylib.inet_ntop(self.ipstart)

    @property
    def ipend_str(self):
        return mylib.inet_ntop(self.ipend)

    @property
    def count(self):
        return self.ipend-self.ipstart+1

class ips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.Integer, nullable=False, unique=True)
    addr_str = db.Column(db.String(15), nullable=False)
    user = db.Column(db.String(64), nullable=False)
    mac = db.Column(db.String(17), nullable=True)
    device = db.Column(db.String(128), nullable=True)
    net = db.Column(db.Integer, db.ForeignKey('nets.id'), nullable=False)
    @property
    def addr_ntop(self):
        return mylib.inet_ntop(self.addr)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    catagory = db.Column(db.String(64), nullable=True)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(32), nullable=True)
    catagory = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    note = db.Column(db.String(64), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), index=True, nullable=True)
