import requests
import secret
import time

payload = {
	"token" : "117780271886003efedddc9f1c9dfa09",
	"type" : "latlng",
	"value" : "40.9459,-74.2451",
	"legislator_id" : "WIL000077"
	#"value" : "27 hinchman ave wayne nj"
}
r = requests.post("http://jayravaliya.com:5000/bills/get", json=payload)

#r = requests.post("http://jayravaliya.com:5000/representatives", json=payload)

#print r.text

#r = requests.post("http://jayravaliya.com:5000/legislators/get", json=payload)
print r.text
