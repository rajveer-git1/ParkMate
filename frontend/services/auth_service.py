from services.client import request


def login(email: str, password: str) -> dict:
    return request(
        "POST", "/users/login", data={"username": email, "password": password}
    )


def get_me(token: str) -> dict:
    return request("GET", "/users/me", token=token)


def register_owner(name, email, phone, password) -> dict:
    return request(
        "POST",
        "/users/register/owner",
        json={"name": name, "email": email, "phone": phone, "password": password},
    )


def register_hotel(name, email, phone, password, hotel: dict) -> dict:
    return request(
        "POST",
        "/users/register/hotel",
        json={
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "hotel": hotel,
        },
    )