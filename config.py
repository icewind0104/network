import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Mount Point
MOUNT_POINT = ''

# flask-wtf
WTF_CSRF_ENABLED = True
SECRET_KEY = '082c8f965947ddb4c2b34730186d0cce'

# db
SQLALCHEMY_TRACK_MODIFICATIONS = True
