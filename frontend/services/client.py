from typing import Optional

import requests

from core.config import API_URL, TIMEOUT_SECONDS


class ApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _error_message(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"Unexpected answer from the server ({response.status_code})"

    detail = body.get("detail") if isinstance(body, dict) else None

    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        parts = []
        for item in detail:
            field = str(item.get("loc", [""])[-1])
            message = str(item.get("msg", "Invalid value")).removeprefix("Value error, ")
            parts.append(f"{field}: {message}")
        return "; ".join(parts)
    return f"The request failed ({response.status_code})"


def request(method, path, *, token=None, json=None, data=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            headers=headers,
            json=json,
            data=data,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.ConnectionError:
        raise ApiError("Cannot reach the ParkMate server. Is the backend running?")
    except requests.exceptions.Timeout:
        raise ApiError("The server took too long to answer. Please try again.")

    if response.status_code >= 400:
        raise ApiError(_error_message(response), response.status_code)
    return response.json()