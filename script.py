import requests
import secret
import time

payload = {
	"token" : "117780271886003efedddc9f1c9dfa09",
	"legislator_id" : "WIL000209"
}
"""
r = requests.post("http://jayravaliya.com:5000/bills/get", json=payload)
"""

r = requests.post("http://jayravaliya.com:5000/legislators/get", json=payload)

print r.text


