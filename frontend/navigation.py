from core.config import MENU_ADD_EDIT_LOT
from views.hotel import bookings as hotel_bookings
from views.hotel import nearby_lots, valets
from views.owner import add_edit_lot, my_lots
from views.owner import bookings as owner_bookings
from views.valet import check_in, parked_cars

MENUS = {
    "owner": {
        "My Lots": my_lots.render,
        MENU_ADD_EDIT_LOT: add_edit_lot.render,
        "Bookings": owner_bookings.render,
    },
    "hotel": {
        "Nearby Lots": nearby_lots.render,
        "Bookings": hotel_bookings.render,
        "Valets": valets.render,
    },
    "valet": {
        "Check in": check_in.render,
        "Parked Cars": parked_cars.render,
    },
}


def menu_for(role: str) -> dict:
    return MENUS[role]