import requests
import json

print('DEBUG DB:')
try:
    r = requests.get('http://localhost:5001/debug/db', timeout=5)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print('Error checking debug/db:', e)

print('\nTRY LOGIN with admin@nuhvin.com / 123456:')
try:
    r2 = requests.post('http://localhost:5001/auth/login', json={'email':'admin@nuhvin.com','password':'123456'}, timeout=5)
    print(r2.status_code)
    try:
        print(json.dumps(r2.json(), indent=2))
    except Exception:
        print(r2.text)
except Exception as e:
    print('Error during login:', e)
