import os
import time
import requests

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5001')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

SERVICES = [
    (BACKEND_URL, '/'),
    (BACKEND_URL, '/debug/db'),
    (FRONTEND_URL, '/'),
]


def check(url, path):
    full = url.rstrip('/') + path
    try:
        r = requests.get(full, timeout=5)
        return r.status_code, r.text[:200]
    except Exception as e:
        return None, str(e)


if __name__ == '__main__':
    print('Running smoke checks...')
    for base, path in SERVICES:
        print(f'Checking {base}{path}...')
        for i in range(30):
            status, body = check(base, path)
            if status and status < 500:
                print(f'  OK: {base}{path} -> {status}')
                break
            else:
                print(f'  waiting for {base}{path} ({status})')
                time.sleep(1)
        else:
            print(f'ERROR: {base}{path} did not respond')
            raise SystemExit(2)
    print('Smoke tests passed!')