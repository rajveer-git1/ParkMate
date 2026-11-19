from services.client import request


def create_valet(token: str, payload: dict) -> dict:
    return request("POST", "/users/valets", token=token, json=payload)