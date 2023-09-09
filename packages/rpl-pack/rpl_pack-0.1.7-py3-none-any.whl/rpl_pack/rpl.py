"""
Base classes for RPL programs mostly for internal use.

"""


import json
import requests
from typing import Any

from rpl_pack.rpl_types import RPLSendType
from rpl_pack.rpl_exceptions import RPLInvalidRequestException


class _RPLBase:
    """Base class that all classes within rpl_pack inherit from.
    
    Docs go here.
    """
    def __init__(self, username: str, password: str, host='127.0.0.1', port='8000', debug=False,
                 prod_addr='rock-physics-lab.herokuapp.com') -> None:
        self.username = username
        self.password = password
        self._auth = (username, password)
        self._host = host
        self._port = port
        self._degub = debug
        self._prod_addr = prod_addr
        if self._degub:
            self._base_url = f'http://{self._host}:{self._port}/api/'
        else:
            self._base_url = f'https://{self._prod_addr}/api/'

    def __str__(self) -> str:
        return 'Base class for all RPL classes.'

    def _is_authentic(self, resp: requests.Response) -> bool:
        """Prevents KeyError on response when not authorized."""
        check = resp.json()
        if isinstance(check, (str,)):
            return True
        if isinstance(check, (dict,)):
            if 'detail' in check: # and check['detail'] == 'Authentication credentials were not provided.':
                return False
        return True

    def _get(self, ext: str) -> requests.Response:
        """Send GET request to RPL server."""
        return requests.get(self._base_url + ext, auth=self._auth)

    def _post(self, ext: str, data: RPLSendType) -> requests.Response:
        """Send POST request to RPL server."""
        # return requests.post(self._base_url + ext, data=data, auth=self._auth)
        # For now we just send json data.
        return requests.post(self._base_url + ext, json=data, auth=self._auth)


    def _put(self, ext: str, data: RPLSendType) -> requests.Response:
        """Send PUT request to RPL server."""
        raise RPLInvalidRequestException('PUT requests are reserved for admins only.')

    def _delete(self, ext: str) -> None:
        """Send DELETE request to RPL server."""
        raise RPLInvalidRequestException('Delete requests are reserved for admins only.')