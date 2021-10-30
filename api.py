from enum import Enum
from typing import Any
import requests
from decouple import config
from functools import lru_cache
from pydantic import BaseModel, validator, UUID4

api_endpoint = config("GRS_API_URL")

class Status(str, Enum):
    draft = 'draft'
    open = 'open'
    replied = 'replied'
    authorResponded = 'authorResponded'
    adminResponded = 'adminResponded'
    closed = 'closed'
    deleted = 'deleted'
    hidden = 'hidden'
    priorityChanged = 'priorityChanged'
    solved = 'solved'
    
class NewResponse(BaseModel):
    post_key: UUID4
    content: str
    status: Status
    user_id: UUID4

class ResponseSerialized(NewResponse):
    post_key: str
    user_id: str

    @validator('post_key', 'user_id', pre=True)
    def validate_uuid(cls, v):
        return v.hex

@lru_cache(maxsize=2)
def get_token():
    """
    Get the Authorization token for Bot Admin User
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(api_endpoint + "/token", data={"username": config("GRS_USERNAME"), "password": config("GRS_PASSWORD")}, headers=headers)
    if response.status_code != 200: return None
    return response.json()['access_token']


def get_user_from_username(username):
    """
    Get the User from username
    """
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(api_endpoint + "/admin/user_from_username/" + username +"/", headers=headers)
    if response.status_code != 200: return None
    return response.json()


def get_user_from_user_id(user_id):
    """
    Get the User from user_id
    """
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(api_endpoint + "/admin/user/" + user_id +"/", headers=headers)
    if response.status_code != 200: return None
    return response.json()


def get_post_from_id(post_id):
    """
    Get the Post from post_id
    """
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(api_endpoint + "/post/" + post_id +"/", headers=headers)
    if response.status_code != 200: return None    
    return response.json()


def add_new_response_to_post(response: NewResponse):
    """
    Add a new response to a post
    """
    headers = {'Authorization': 'Bearer ' + get_token(), 'Content-Type': 'application/json'}
    response = requests.post(api_endpoint + "/posts/response/new/", json=ResponseSerialized(**response.dict()).dict(), headers=headers)
    if response.status_code != 200: return None
    return response.json()
