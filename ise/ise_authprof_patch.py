""" ISE Python script to patch authorization profiles
"""

__author__ = "p3rh0ps"
__copyright__ = "Copyright 2022, p3rh0ps"
__credits__ = ["p3rh0ps"]
__license__ = "MIT"
__version__ = "0.91"
__maintainer__ = "p3rh0ps"
__email__ = "p3rh0ps@gmail.com"
__status__ = "prototype"

import requests
import json

API_PROTO  = "https"
ISE_HOST = "10.0.0.1"
API_PORT = "443"
RESOURCE = "ers/config/authorizationprofile"

url = f"{API_PROTO}://{ISE_HOST}:{API_PORT}/{RESOURCE}"
auth = "ers","MySuperPassword"
headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}
    
def retrieve_auth_profiles(url) -> list:
    """ Retrieve Authorization Profiles from ISE
    """
    payload_get = {}
    auth_profiles = []

    while (url) :
        resp_get = requests.get(\
        url, auth=auth, headers=headers, data=payload_get, verify=False)
        auth_profiles += resp_get.json()["SearchResult"]["resources"]
        try :
            resp_get.raise_for_status()
            url = resp_get.json()["SearchResult"]["nextPage"]["href"]
        except Exception as e :
            print(e)
            url = None
    return auth_profiles


def patch_auth_profile(prof_id: str, payload: dict) -> None:
    
    """ Patch Authorization Profiles by ID in ISE
        with specific payload_patch
    """ 
    RESOURCE_PATCH = f'ers/config/authorizationprofile/{prof_id}'
    url = f"{API_PROTO}://{ISE_HOST}:{API_PORT}/{RESOURCE_PATCH}"

    resp_patch = requests.patch(\
    url, auth=auth, headers=headers, data=payload, verify=False)

def main():

    authprof_lst = retrieve_auth_profiles(url)

    payload_patch = {
           "AuthorizationProfile": {
             "reauth" : {
               "timer" : 65000,
               "connectivity" : "RADIUS_REQUEST"
               }
             }
           }

    for idx in range(0, len(authprof_lst)):
        patch_auth_profile(authprof_lst[idx]["id"], payload_patch)

if __name__ == "__main__":
    main()
