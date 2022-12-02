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

import json
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

API_PROTO  = "https"
ISE_HOST = "64.103.46.211"
API_PORT = "9060"
RESOURCE = "ers/config/authorizationprofile"
METHOD = "PUT"

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
            url = None
    return auth_profiles

def retrieve_auth_profile_config(prof_id: str) -> dict:
    """ Retrieve Authorization Profile Configuration
        By ID
    """
    payload_get = {}
    RESOURCE_GET = f"ers/config/authorizationprofile/{prof_id}"
    url = f"{API_PROTO}://{ISE_HOST}:{API_PORT}/{RESOURCE_GET}"
    
    resp_get_conf_id = requests.get(\
    url, auth=auth, headers=headers, data=payload_get, verify=False)
    print(json.dumps(resp_get_conf_id.json(), indent=4))
    return resp_get_conf_id.json()


def update_auth_profile(method: str, prof_id: str, payload: dict) -> None:
    """ Patch Authorization Profiles by ID in ISE
        with specific payload_patch
    """
    RESOURCE = f'ers/config/authorizationprofile/{prof_id}'

    url = f"{API_PROTO}://{ISE_HOST}:{API_PORT}/{RESOURCE}"
    
    resp = requests.request(\
    method, url, auth=auth, headers=headers, data=payload, verify=False)
    print(resp.request.url)
    print(resp.request.headers)
    resp.raise_for_status()


def main():
    """ Main Function
    """
    authprof_lst = retrieve_auth_profiles(url)

    change_to_pass = {
            "reauth" : {
               "timer" : 10000,
               "connectivity" : "RADIUS_REQUEST"
               }
             }

    payload_patch = { "AuthorizationProfile":  {
                        }
                    }

    payload_patch["AuthorizationProfile"].update(change_to_pass)

    for idx in range(0, len(authprof_lst)):
        if METHOD == "PATCH":
            update_auth_profile(METHOD,authprof_lst[idx]["id"], payload_patch)
        if METHOD == "PUT":
            payload_put = retrieve_auth_profile_config(authprof_lst[idx]["id"])
            payload_put["AuthorizationProfile"].update(change_to_pass)
            print(json.dumps(payload_put, indent=4))
            #print(payload_put)
            update_auth_profile(METHOD,authprof_lst[idx]["id"], payload_put)

if __name__ == "__main__":
    main()
