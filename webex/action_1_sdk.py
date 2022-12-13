import os
from webexteamssdk import WebexTeamsAPI

api = WebexTeamsAPI(access_token=os.environ.get("WEBEX_TOKEN"))
print(api.people.me())

""" Comparison with requests library
import requests

apiUrl = 'https://webexapis.com/v1/people/me'
access_token = '<your_access_token>'

httpHeaders = {'Authorization': 'Bearer ' + access_token,
           'Content-type': 'application/json'}
body = {'roomId': ROOM_ID, 'text': MESSAGE_TEXT}
response = requests.get(apiUrl, headers=httpHeaders)
if response.status_code == 200:
    print(response.text)
else:
    # Oops something went wrong...  Better do something about it.
    print(response.status_code, response.text)
"""

room = api.rooms.create("WebEx SDK created room")
print(room)
api.memberships.create(room.id, personEmail="p3rBot@webex.bot")
api.messages.create(room.id,\
text="**I am an IT-Professional, and I have completed this challenge!!!**")
