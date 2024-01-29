"""Module for handling Aquarite API."""
import datetime
from http import HTTPStatus
import json
from typing import Any

import aiohttp
import logging
from aiohttp import ClientResponseError
from aiohttp.client import ClientResponse
from google.cloud.firestore import Client, DocumentSnapshot
from google.oauth2.credentials import Credentials
import requests
from requests import HTTPError

__title__ = "Aquarite"
__version__ = "1.0.0"
__author__ = "Tobias Laursen"
__license__ = "MIT"

API_KEY = "AIzaSyBLaxiyZ2nS1KgRBqWe-NY4EG7OzG5fKpE"
GOOGLE_IDENTITY_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"
HAYWARD_REST_API = "https://europe-west1-hayward-europe.cloudfunctions.net/"

_LOGGER = logging.getLogger(__name__)

class Aquarite:
    """Aquarite API."""

    def __init__(self, aiohttp_session: aiohttp.ClientSession, username : str, password : str)-> None:
        """Init Aquarite API."""
        self.aiohttp_session: aiohttp.ClientSession = aiohttp_session
        self.username = username
        self.password = password
        self.tokens = None
        self.expiry = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.credentials = Credentials | None
        self.client = Client | None
        self.handlers = []

    @classmethod
    async def create(cls, aiohttp_session: aiohttp.ClientSession, username : str, password : str):
        """Initiate Aquarite async."""
        instance = cls(aiohttp_session, username, password)
        await instance.signin()
        instance.credentials = Credentials(token=instance.tokens["idToken"], expiry=instance.expiry, refresh_handler=instance.get_token_and_expiry )
        instance.client = Client(project="hayward-europe", credentials=instance.credentials)
        return instance


    def get_token_and_expiry(self, request, scopes) -> Any:
        """Return the token as json."""
        request_url = f"{GOOGLE_IDENTITY_REST_API}:signInWithPassword?key={API_KEY}"
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps(
            {"email": self.username, "password": self.password, "returnSecureToken": True}
        )

        req = requests.post(request_url, headers=headers, data=data, timeout=60)
        # Check for errors
        try:
            req.raise_for_status()
        except HTTPError as e:
            raise UnauthorizedException(e, req.text) from e

        self.tokens = req.json()
        self.expiry = datetime.datetime.now() + datetime.timedelta(seconds=int(self.tokens["expiresIn"]))

        return self.tokens["idToken"], self.expiry

    async def signin(self):
        """Signin."""
        try:
            resp: ClientResponse = await self.aiohttp_session.post(
                f"{GOOGLE_IDENTITY_REST_API}:signInWithPassword?key={API_KEY}",
                json ={"email": self.username, "password": self.password, "returnSecureToken": True}
            )
            if resp.status == 400:
                raise UnauthorizedException(resp.reason)
            self.tokens = await resp.json()
            self.expiry = datetime.datetime.now() + datetime.timedelta(seconds=int(self.tokens["expiresIn"]))
        except ClientResponseError as err:
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise UnauthorizedException(err) from err


    async def get_pools(self):
        """Get all pools for current user."""
        data = {}
        user_dict = (
            self.client.collection("users").document(self.tokens["localId"]).get().to_dict()
        )
        for poolId in user_dict["pools"]:
            pooldict = self.client.collection("pools").document(poolId).get().to_dict()
            if pooldict is not None:
                data[poolId] = pooldict["form"]["name"]
        return data

    def get_pool(self, pool_id)-> DocumentSnapshot:
        """Get pool by pool id."""
        return self.client.collection("pools").document(pool_id).get()

    def subscribe(self, pool_id, handler) -> None:
        """Add subscriber on pool."""
        doc_ref = self.client.collection("pools").document(pool_id)
        doc_ref.on_snapshot(self.__on_snapshot)
        self.handlers.append(handler)

    async def turn_on_light(self, pool_id)-> None:
        """Turn on light."""
        pool_data = self.__get_pool_as_json(pool_id)
        pool_data['pool']['light']['status'] = 1
        pool_data['changes'] = [{"kind": "E", "path": ["light", "status"], "lhs": 0, "rhs": 1}]
        await self.__send_command(pool_data)

    async def turn_off_light(self, pool_id)-> None:
        """Turn off light."""
        pool_data = self.__get_pool_as_json(pool_id)
        pool_data['pool']['light']['status'] = 0
        pool_data['changes'] = [{"kind": "E", "path": ["light", "status"], "lhs": 1, "rhs": 0}]
        await self.__send_command(pool_data)

    async def turn_on_relay(self, pool_id, name)-> None:
        """Turn on relay"""
        pool_data = self.__get_pool_as_json(pool_id)
        pool_data['pool']['relays']['' + name.lower() + '']['info']['onoff'] = 1
        pool_data['changes'] = '[{"kind": "E", "path": ["relays", "' + name.lower() + '", "info", "onoff"], "lhs": 0, "rhs": 1}]'
        await self.__send_command(pool_data)

    async def turn_off_relay(self, pool_id, name)-> None:
        """Turn off relay"""
        pool_data = self.__get_pool_as_json(pool_id)
        pool_data['pool']['relays']['' + name.lower() + '']['info']['onoff'] = 0
        pool_data['changes'] = '[{"kind": "E", "path": ["relays",  "' + name.lower() + '", "info", "onoff"], "lhs": 1, "rhs": 0}]'
        await self.__send_command(pool_data)
    
    async def __send_command(self, data)-> None:
        headers = {"Authorization": "Bearer "+self.tokens["idToken"]}
        await self.aiohttp_session.post(
                f"{HAYWARD_REST_API}/sendCommand",
                json = data,
                headers=headers
                )

    def __get_pool_as_json(self, pool_id):
        pool = self.get_pool(pool_id)
        data = {"gateway" : pool.get("wifi"),
                "operation" : "WRP",
                "operationId" : None,
                "pool": {"backwash": pool.get("backwash"),
                         "filtration": pool.get("filtration"),
                         "hidro" : pool.get("hidro"),
                         "light" : pool.get("light"),
                         "main" : pool.get("main"),
                         "relays" : pool.get("relays")
                        },
                "poolId" : pool_id,
                "source" : "web"}
        _LOGGER.debug(data)
        return data


    def __on_snapshot(self, doc_snapshot, changes, read_time) -> None:
        """Create a callback on_snapshot function to capture changes."""
        for doc in doc_snapshot:
            for handler in self.handlers:
                handler(doc)

class UnauthorizedException(Exception):
    """Unauthorized user exception."""
