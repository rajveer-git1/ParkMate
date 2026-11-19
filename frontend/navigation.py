from views.common import home

MENUS = {
    "owner": {"Home": home.render},
    "hotel": {"Home": home.render},
    "valet": {"Home": home.render},
}


def menu_for(role: str) -> dict:
    return MENUS[role]