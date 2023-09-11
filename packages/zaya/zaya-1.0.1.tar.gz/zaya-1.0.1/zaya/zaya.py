import requests

def connect(token):
    global header
    header = {'Content-Type':'Content-Type: application/x-www-form-urlencoded', 'Authorization': f'Authorization: Bearer {token}'}

def all_url():
    req = requests.get("https://zaya.io/api/v1/links", headers=header)
    return req.json().get('data')

def create_url(url):
    req = requests.post("https://zaya.io/api/v1/links", headers=header, params={'url':url})
    return req.json().get('data')

def detail_url(id):
    req = requests.get(f"https://zaya.io/api/v1/links/{id}", headers=header)
    return req.json().get('data')

def update_url(id, url):
    req = requests.put(f"https://zaya.io/api/v1/links/{id}", headers=header, params={'url':url})
    return req.json().get('data')

def delete_url(id):
    req = requests.delete(f"https://zaya.io/api/v1/links/{id}", headers=header)
    return req.json()

# __________________________________________________ domain ____________________________________________________

def all_domain():               # domaneh haye zaya ro neshoon mideh
    req = requests.get("https://zaya.io/api/v1/domains", headers=header)
    return req.json().get('data')

def create_domain(domain):
    req = requests.post("https://zaya.io/api/v1/domains", headers=header, params={'name':domain})
    return req.json().get('data')

def details_domain(id):
    req = requests.get(f"https://zaya.io/api/v1/domains/{id}", headers=header)
    return req.json().get('data')

def update_domain(id, domain):             # domain edit nemikhore
    req = requests.put(f"https://zaya.io/api/v1/domains/{id}", headers=header, params={'name':domain})
    return req.json().get('data')

def delete_domain(id):
    req = requests.delete(f"https://zaya.io/api/v1/domains/{id}", headers=header)
    return req.json()

def account():
    req = requests.get(f"https://zaya.io/api/v1/account", headers=header)
    return req.json().get('data')

for key, value in account().items():
    print(key, value)