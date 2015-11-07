import requests
import secret
import time

payload = {
	"token" : "117780271886003efedddc9f1c9dfa09",
	"type" : "address",
	"value" : "40.9459,-74.2451"
	#"value" : "27 hinchman ave wayne nj"
}
"""
r = requests.post("http://jayravaliya.com:5000/bills/get", json=payload)
"""

r = requests.post("http://jayravaliya.com:5000/representatives", json=payload)

print r.text


