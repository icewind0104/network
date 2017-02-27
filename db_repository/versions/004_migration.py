from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
ips = Table('ips', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('addr', Integer, nullable=False),
    Column('user', String(length=64), nullable=False),
    Column('mac', String(length=17)),
    Column('device', String(length=128)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ips'].columns['device'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['ips'].columns['device'].drop()
