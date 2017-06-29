from app import db, mylib
import time

class departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ipstart = db.Column(db.Integer)
    ipend = db.Column(db.Integer)
    parent = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete="CASCADE"), nullable=True)
    employees = db.relationship('employees', backref='department', lazy='dynamic')

class employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.Boolean)
    hosts = db.relationship('hosts', backref='hosts_user', lazy='dynamic')
    displays = db.relationship('displays', backref='displays_user', lazy='dynamic')
    laptops = db.relationship('laptops', backref='laptops', lazy='dynamic')
    ips = db.relationship('ips', backref='ips_user', lazy='dynamic', cascade="delete")
    def to_dict(self):
        return {'id':self.id, 'name':self.name, 'department_id':self.department_id, 'status':self.status}

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
    mac = db.Column(db.String(17), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
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

#class assets(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    serial = db.Column(db.String(32), nullable=True)
#    catagory = db.Column(db.String(32), nullable=False)
#    name = db.Column(db.String(128), nullable=False)
#    note = db.Column(db.String(64), nullable=True)
#    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    
class hosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Float, nullable=True, default=time.time())
    cpu = db.Column(db.String(32), nullable=True)
    memory = db.Column(db.String(16), nullable=True)
    motherboard = db.Column(db.String(32), nullable=True)
    graphics = db.Column(db.String(32), nullable=True)
    note = db.Column(db.String(64), nullable=True)
    asset_sn = db.Column(db.String(32), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    
class displays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Float, nullable=True, default=time.time())
    vendor = db.Column(db.String(16), nullable=True)
    model = db.Column(db.String(16), nullable=True)
    serial = db.Column(db.String(32), nullable=True)
    note = db.Column(db.String(64), nullable=True)
    asset_sn = db.Column(db.String(32), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    
class laptops(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Float, nullable=True, default=time.time())
    vendor = db.Column(db.String(16), nullable=True)
    model = db.Column(db.String(16), nullable=True)
    serial = db.Column(db.String(32), nullable=True)
    note = db.Column(db.String(64), nullable=True)
    asset_sn = db.Column(db.String(32), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)