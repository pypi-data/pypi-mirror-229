import base64
import json
import os
from pathlib import Path
from typing import Callable

import requests

from korbit.interface import INTERFACE_AUTH_MISSING_CREDENTIALS_MSG

KORBIT_CREDENTIAL_FILE = os.path.expanduser("~/.korbit/credentials")


def store_credentials(secret_id, secret_key):
    """
    Store user credentials for future usage of scan command.
    """
    os.makedirs(Path(KORBIT_CREDENTIAL_FILE).parent, exist_ok=True)
    with open(KORBIT_CREDENTIAL_FILE, "w+") as credential_file:
        json.dump({"secret_id": secret_id, "secret_key": secret_key}, credential_file)


def compute_user_token():
    credentials = {}
    if os.path.exists(KORBIT_CREDENTIAL_FILE):
        with open(KORBIT_CREDENTIAL_FILE, "r+") as credential_file:
            credentials = json.loads(credential_file.read())
    secret_id = os.getenv("KORBIT_SECRET_ID", credentials.get("secret_id"))
    secret_key = os.getenv("KORBIT_SECRET_KEY", credentials.get("secret_key"))
    assert secret_id, INTERFACE_AUTH_MISSING_CREDENTIALS_MSG
    assert secret_key, INTERFACE_AUTH_MISSING_CREDENTIALS_MSG
    return base64.b64encode(f"{secret_id}:{secret_key}".encode()).decode()


def authenticate_request(method: Callable[[str], requests.Response], url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    if not headers.get("Authorization"):
        headers["Authorization"] = f"Basic {compute_user_token()}"
    kwargs["headers"] = headers
    response = method(url, **kwargs)
    response.raise_for_status()
    return response
