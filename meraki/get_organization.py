import requests

#token = '6bec40cf957de430a6f1f2baa056b99a4fac9ea0'
token = 'fd6dd87d96915f21bc0e0b3d96a866ff0e53e381'

headers = {
    'X-Cisco-Meraki-API-Key': token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# MERAKI BASE URL
base_url = "https://api.meraki.com/api/v0"

def get_organizations():
    orgs_url = '/organizations'
    response = requests.get(base_url + orgs_url, headers=headers)
    for idx in range(0, len(response.json())):
        print(response.json()[idx]['id'])

if __name__ == "__main__":
    get_organizations()
