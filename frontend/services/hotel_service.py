from services.client import request


def my_hotel(token: str) -> dict:
    return request("GET", "/hotels/me", token=token)