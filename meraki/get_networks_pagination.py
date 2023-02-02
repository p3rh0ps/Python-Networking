import requests

token = 'fd6dd87d96915f21bc0e0b3d96a866ff0e53e381'

headers = {
    'X-Cisco-Meraki-API-Key': token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# MERAKI BASE URL
base_url = "https://api.meraki.com/api/v1"
paginate = "?perPage=5"

def get_networks():
    nets_url = '/organizations/549236/networks'
    response = requests.get(base_url + nets_url + paginate, headers=headers)
    print(response.headers)
    print("-"*79)
    print("-"*79)
    
    while response.links.get("next"):
        print(response.links)
        url = response.links["next"]["url"]
        response = requests.get(url, headers=headers)
        print("*"*79)


if __name__ == "__main__":
    get_networks()
