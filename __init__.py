# Flask Boilerplate
# By Jay Ravaliya

from flask import Flask, make_response, jsonify, request, abort, render_template
import requests
import secret
from model import db, Users, Tags
import hashlib
import json
import sys

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
	return make_response(jsonify({"Success" : "Hello, world!"}), 200)

@app.route("/register", methods=['POST'])
def register():
	data = request.get_json()
	if 'email' not in data or 'password' not in data:
		return make_response(jsonify({"Error" : "Invalid parameters."}), 400)
	else:
		user = Users.query.filter_by(email=data['email']).first()
		if user:
			return make_response(jsonify({"Error" : "User already exists."}), 400)
		else:
			user = Users(data['email'], data['password'])
			token = user.token
			db.session.add(user)
			db.session.commit()	
			return make_response(jsonify({"Success" : token}), 200)

@app.route("/login", methods=['POST'])
def login():
	data = request.get_json()
	if 'email' not in data or 'password' not in data: 
		return make_response(jsonify({"Error" : "Invalid parameters."}), 400)
	else:
		user = Users.query.filter_by(email=data['email']).filter_by(password=hashlib.md5(data['password']).hexdigest()).first()
		if not user:
			return make_response(jsonify({"Error" : "Invalid credentials."}), 400)
		else:
			return make_response(jsonify({"Success" : user.token}), 200)

@app.route("/tags", methods=['POST'])
def getTags():
	data = request.get_json()
	if 'token' not in data:
		return make_response(jsonify({"Error" : "Unauthorized."}), 400)
	else:
		user = Users.query.filter_by(token=data['token']).first()
		if not user:
			return make_response(jsonify({"Error" : "Invalid user"}), 400)
		else:
			arr = []
			for elem in user.tags:
				arr.append(elem.tag)
			return make_response(jsonify({"Success" : arr}), 200)

@app.route("/tags/add", methods=['POST'])
def addTag():
	data = request.get_json()
	if not data['token']:
		return make_response(jsonify({"Error" : "Unauthorized."}), 400)
	elif not data['tag']:
		return make_response(jsonify({"Error" : "Invalid parameters."}), 400)
	else:
		user = Users.query.filter_by(token=data['token']).first()
		if not user:
			return make_response(jsonify({"Error" : "Invalid user."}), 400)
		else:
			tag = Tags.query.filter_by(tag=data['tag']).first()
			if tag:
				return make_response(jsonify({"Success" : "Tag already existed."}), 200)
			else:
				tag = Tags(data['tag'])
				user.tags.append(tag)
				db.session.commit()
				return make_response(jsonify({"Success" : "Tag added: " + data['tag']}), 200)

@app.route("/tags/remove", methods=['POST'])
def removeTag():
	data = request.get_json()
	if not data['token']:
		return make_response(jsonify({"Error" : "Unauthorized."}), 400)
	elif not data['tag']:
		return make_response(jsonify({"Error" : "Invalid parameters."}), 400)
	else:
		user = Users.query.filter_by(token=data['token']).first()
		if not user:
			return make_response(jsonify({"Error" : "Invalid user."}), 400)
		else:
			tag = Tags.query.filter_by(tag=data['tag']).first()
			if not tag:
				return make_response(jsonify({"Success" : "Tag never existed."}), 200)
			else:
				db.session.delete(tag)
				db.session.commit()
				return make_response(jsonify({"Success" : "Tag deleted: " + data['tag']}), 200)

@app.route("/bills/get", methods=['POST'])
def getBills():
	print "Request processing..."
	data = request.get_json()
	if not data['token']:
		return make_response(jsonify({"Error" : "Unauthorized."}), 400)
	else:
		user = Users.query.filter_by(token=data['token']).first()
		if not user:
			return make_response(jsonify({"Error" : "Invalid user."}), 400)
		else:
			result = []
			for tag in user.tags:
				print "Working on tag: " + tag.tag
				result.append({tag.tag : apiBills(tag.tag)})
 
			return make_response(jsonify({"Success" : result}), 200)

def apiBills(tag):
	print "Getting bills for tag: " + tag
	payload = {
		"q" : tag,
		"count" : 10,
		"page" : 0,
		"sortby" : "lastactiondate",
		"order" : "desc",
		"apikey" : secret.FNAPI
	}
 
	r = requests.get("https://api.fiscalnote.com/bills", params=payload, timeout=5)
	arr = []

	print "Received bills for tag: " + tag + ". Getting details..."

	for element in r.json():
		id = str(element['id'])

		print "Working on id " + id + " for tag " + tag

		s = requests.get("https://api.fiscalnote.com/bill/" + id, params={"apikey":secret.FNAPI}, timeout=2)
		print "Request on id " + id + " for tag " + tag + " complete. Converting to JSON and objectifying"
		s = s.json()

		def return_sources(s):
			obj = []
			for elem in s:
				dictionary = {
					"mimetype": elem['mimetype'],
					"url": elem['url'],
					"doc_id": elem['doc_id'],
					"name": elem['name']
				}
				obj.append(dictionary)
			return obj 

		def return_lid(s):
			obj = []
			if 'sponsors' not in s:
				return {}
			for elem in s['sponsors']:
				obj.append({"legislator_id": elem["legislator_id"]})
			return obj

		obj = {
			"id" : id,
			"title" : s['title'],
			"prefloor_probability" : s['prefloor_probability'],
			"postfloor_probability" : s['postfloor_probability'],
			"current_prediction" : s['current_prediction'],
			"sources" : return_sources(s['bill_texts']),
			"lastaction" : s["bill_action_dates"]["last_action"],
			"sponsors": return_lid(s["current_prediction_analysis"])
		}

		print "Object built for id " + id + " tag " + tag

		arr.append(obj.copy())
	
	return arr

@app.route("/legislators/get", methods=['POST'])
def getLegislators():
	data = request.get_json()
	if 'token' not in data or 'legislator_id' not in data:
		return make_response(jsonify({"Error":"Invalid parameters."}), 400)
	else:
		user = Users.query.filter_by(token=data['token']).first()
		if not user:
			return make_response(jsonify({"Error":"Invalid user."}), 400)
		else:
			payload = {
				"apikey":secret.FNAPI
			}
			r = requests.get("https://api.fiscalnote.com/legislator/" + data['legislator_id'], params=payload, timeout=5)
			print r.text
			return jsonify(**r.json())

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
