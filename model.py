# Flask Boilerplate
# By Jay Ravaliya

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

import secret
import hashlib
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secret.SQLITE_KEY

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('fn', MigrateCommand)

class Users(db.Model):

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String)
	password = db.Column(db.String)
	token = db.Column(db.String)
	tags = relationship("Tags", backref="users", primaryjoin=("Users.id==Tags.user_id"))
	bills = relationship("Bills", backref="users", primaryjoin=("Users.id==Bills.user_id"))

	def __init__(self, email, password): 
		self.email = email 
		self.password = hashlib.md5(password).hexdigest()
		self.token = hashlib.md5(email + ";" + password + ";" + str(time.time())).hexdigest()

class Tags(db.Model):
	
	__tablename__ = "tags"

	id = db.Column(db.Integer, primary_key=True)
	tag = db.Column(db.String)
	user_id = db.Column(db.Integer, ForeignKey('users.id'))

	def __init__(self, tag):
		self.tag = tag

class Bills(db.Model):

	__tablename__ = "new"

	id = db.Column(db.Integer, primary_key=True)
	bill_id = db.Column(db.Integer)
	user_id = db.Column(db.Integer, ForeignKey('users.id'))

	def __init__(self, bill_id):
		self.bill_id = bill_id

if __name__ == "__main__":
	manager.run()
