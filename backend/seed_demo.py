import sys
from datetime import datetime, timedelta

from app import models
from app.core.enums import BookingStatus, UserRole
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.utils.billing import calculate_fee
from app.utils.geo import parse_coordinates
from app.utils.security import hash_password

DEMO_PASSWORD = "demo1234"
EMAIL_DOMAIN = "parkmate-demo.com"
CITY = "Indore"

OWNERS = {
    "rakesh": "Rakesh Joshi",
    "neha": "Neha Agrawal",
    "imran": "Imran Qureshi",
}

HOTELS = {
    "rajwada": {
        "name": "Rajwada Heritage Inn",
        "address": "Near Rajwada Palace, Old City",
        "coordinates": "22.7190, 75.8560",
        "staff": ("anil", "Anil Verma"),
        "valets": [("ramesh", "Ramesh Yadav"), ("sunil", "Sunil Patel")],
    },
    "palasia": {
        "name": "Palasia Park Hotel",
        "address": "New Palasia, near 56 Dukan",
        "coordinates": "22.7240, 75.8835",
        "staff": ("pooja", "Pooja Sharma"),
        "valets": [("deepak", "Deepak Chouhan"), ("kunal", "Kunal Dubey")],
    },
    "vijay": {
        "name": "Vijay Nagar Suites",
        "address": "Vijay Nagar Square, AB Road",
        "coordinates": "22.7535, 75.8940",
        "staff": ("rohit", "Rohit Mishra"),
        "valets": [("arjun", "Arjun Rathore"), ("mohit", "Mohit Tiwari")],
    },
}

# key: (owner, name, address, coordinates, total slots, price per hour, active)
LOTS = {
    "plaza": ("rakesh", "Rajwada Parking Plaza", "Near Rajwada Palace, Old City",
              "22.7178, 75.8548", 40, 20, True),
    "sarafa": ("rakesh", "Sarafa Night Parking", "Near Sarafa Bazaar, Old City",
               "22.7173, 75.8562", 25, 30, True),
    "chhappan": ("rakesh", "Chhappan Dukan Mini Lot", "New Palasia, near 56 Dukan",
                 "22.7236, 75.8828", 3, 25, True),
    "palasia_sq": ("rakesh", "Palasia Square Lot", "Palasia Square (closed for repairs)",
                   "22.7232, 75.8845", 20, 25, False),
    "vn_square": ("neha", "Vijay Nagar Square Parking", "Vijay Nagar Square, AB Road",
                  "22.7532, 75.8937", 60, 30, True),
    "scheme54": ("neha", "Scheme 54 Parking Hub", "Scheme No. 54, Vijay Nagar",
                 "22.7530, 75.8921", 50, 35, True),
    "scheme74": ("neha", "Scheme 74 Open Lot", "Scheme No. 74, Vijay Nagar",
                 "22.7590, 75.8891", 45, 25, True),
    "station": ("imran", "Railway Station Parking", "Near Indore Junction railway station",
                "22.7167, 75.8678", 80, 15, True),
    "airport": ("imran", "Airport Road Parking", "Near Devi Ahilya Bai Holkar Airport",
                "22.7218, 75.8011", 70, 40, True),
    "bhawarkuan": ("imran", "Bhawarkuan Square Lot", "Bhawarkuan Square, AB Road",
                   "22.6906, 75.8696", 35, 20, True),
}

# (hotel, valet, lot, guest, car number, model, colour, minutes ago, minutes parked)
# "minutes parked" of None means the car is still parked.
BOOKINGS = [
    ("rajwada", "ramesh", "plaza", "Ankit Saxena", "MP09CD4521", "Maruti Swift", "White", 95, None),
    ("rajwada", "sunil", "sarafa", "Priya Jain", "MP09AB7788", "Hyundai Creta", "Black", 40, None),
    ("rajwada", "ramesh", "plaza", "Vikram Singh Rathore", "RJ14CK2210", "Toyota Innova Crysta", "Silver", 210, None),
    ("palasia", "deepak", "chhappan", "Sneha Kulkarni", "MH12DE9034", "Honda City", "Red", 55, None),
    ("palasia", "kunal", "chhappan", "Rahul Mehta", "GJ01KM4410", "Tata Nexon", "Blue", 120, None),
    ("palasia", "deepak", "chhappan", "Farhan Sheikh", "MP09ZZ1305", "Kia Seltos", "Grey", 25, None),
    ("palasia", "kunal", "station", "Meera Nair", "KA03MN6672", "Maruti Baleno", "White", 330, None),
    ("vijay", "arjun", "vn_square", "Karan Malhotra", "DL01AB1290", "Mahindra XUV700", "Black", 75, None),
    ("vijay", "mohit", "scheme54", "Aditi Deshmukh", "MH14FG3321", "Hyundai i20", "Orange", 150, None),
    ("vijay", "arjun", "vn_square", "Siddharth Rao", "TS09BC7755", "Maruti Brezza", "Grey", 45, None),
    ("vijay", "mohit", "scheme74", "Neelam Gupta", "MP09GH2468", "Honda Amaze", "Silver", 600, None),
    ("vijay", "arjun", "airport", "Ravi Shankar", "MP04XY5566", "Toyota Fortuner", "White", 1500, None),
    ("rajwada", "ramesh", "plaza", "Suresh Agarwal", "MP09HJ1122", "Maruti Alto", "Grey", 1500, 180),
    ("rajwada", "sunil", "sarafa", "Kavita Bansal", "MP09LM3344", "Hyundai Venue", "Blue", 1480, 95),
    ("rajwada", "ramesh", "station", "Manoj Tripathi", "UP32RT8812", "Mahindra Scorpio", "Black", 2900, 1500),
    ("palasia", "deepak", "chhappan", "Isha Kapoor", "MP09PQ6677", "Honda City", "White", 1400, 130),
    ("palasia", "kunal", "chhappan", "Gaurav Patidar", "MP09ST9900", "Tata Punch", "Green", 1350, 45),
    ("palasia", "deepak", "plaza", "Nisha Verma", "MH31UV1020", "Maruti Ertiga", "Silver", 2800, 240),
    ("palasia", "kunal", "station", "Harsh Vardhan", "GJ05WX3456", "Hyundai Creta", "Red", 2700, 600),
    ("vijay", "arjun", "vn_square", "Pallavi Joshi", "MP09YZ7788", "Kia Sonet", "Blue", 1300, 205),
    ("vijay", "mohit", "scheme54", "Abhishek Nair", "KA51AA2020", "Toyota Glanza", "White", 1250, 60),
    ("vijay", "arjun", "airport", "Tanvi Bhatt", "MH02BB3030", "Honda City", "Grey", 2600, 360),
    ("vijay", "mohit", "scheme74", "Dev Malik", "HR26CC4040", "Skoda Slavia", "Black", 2500, 150),
    ("vijay", "arjun", "vn_square", "Shweta Pandey", "MP09DD5050", "Maruti Swift", "Red", 4200, 90),
    ("rajwada", "sunil", "bhawarkuan", "Alok Dubey", "MP09EE6060", "Tata Harrier", "Grey", 4100, 270),
    ("palasia", "deepak", "bhawarkuan", "Rekha Soni", "MP09FF7070", "Maruti Wagon R", "White", 3000, 120),
]


def email_for(key: str, role: UserRole) -> str:
    return f"{key}.{role.value}@{EMAIL_DOMAIN}"


def seed(db) -> None:
    password_hash = hash_password(DEMO_PASSWORD)
    phone_numbers = iter(range(1, 10_000))

    def next_phone() -> str:
        return f"9000{next(phone_numbers):06d}"

    def add_user(key, name, role, hotel_id=None):
        user = models.User(
            name=name,
            email=email_for(key, role),
            phone=next_phone(),
            password_hash=password_hash,
            role=role.value,
            hotel_id=hotel_id,
        )
        db.add(user)
        db.flush()
        return user

    owners = {
        key: add_user(key, name, UserRole.OWNER) for key, name in OWNERS.items()
    }

    hotels = {}
    valets = {}
    for key, data in HOTELS.items():
        latitude, longitude = parse_coordinates(data["coordinates"])
        hotel = models.Hotel(
            name=data["name"],
            address=data["address"],
            city=CITY,
            latitude=latitude,
            longitude=longitude,
        )
        db.add(hotel)
        db.flush()
        hotels[key] = hotel

        staff_key, staff_name = data["staff"]
        add_user(staff_key, staff_name, UserRole.HOTEL, hotel.id)
        for valet_key, valet_name in data["valets"]:
            valets[valet_key] = add_user(valet_key, valet_name, UserRole.VALET, hotel.id)

    lots = {}
    for key, (owner, name, address, coordinates, slots, price, active) in LOTS.items():
        latitude, longitude = parse_coordinates(coordinates)
        lot = models.ParkingLot(
            owner_id=owners[owner].id,
            name=name,
            address=address,
            city=CITY,
            latitude=latitude,
            longitude=longitude,
            total_slots=slots,
            price_per_hour=price,
            is_active=active,
        )
        db.add(lot)
        db.flush()
        lots[key] = lot

    now = datetime.now()
    parked_per_lot = {}
    for (hotel_key, valet_key, lot_key, guest, car, model, colour,
         minutes_ago, minutes_parked) in BOOKINGS:
        lot = lots[lot_key]
        check_in = now - timedelta(minutes=minutes_ago)
        booking = models.Booking(
            hotel_id=hotels[hotel_key].id,
            lot_id=lot.id,
            valet_id=valets[valet_key].id,
            guest_name=guest,
            guest_phone=next_phone(),
            vehicle_number=car,
            vehicle_model=model,
            vehicle_color=colour,
            price_per_hour=lot.price_per_hour,
            check_in_time=check_in,
        )
        if minutes_parked is None:
            booking.status = BookingStatus.PARKED.value
            parked_per_lot[lot_key] = parked_per_lot.get(lot_key, 0) + 1
        else:
            check_out = check_in + timedelta(minutes=minutes_parked)
            booking.check_out_time = check_out
            booking.total_fee = calculate_fee(check_in, check_out, lot.price_per_hour)
            booking.status = BookingStatus.COMPLETED.value
        db.add(booking)

    for lot_key, parked in parked_per_lot.items():
        if parked > LOTS[lot_key][4]:
            raise ValueError(f"Seed data puts too many cars in lot '{lot_key}'")


def print_summary() -> None:
    print()
    print("Demo data created.")
    print(f"Every account uses the password: {DEMO_PASSWORD}")
    print()
    print("Owners")
    for key, name in OWNERS.items():
        print(f"  {email_for(key, UserRole.OWNER):<38} {name}")
    print()
    print("Hotel staff and valets")
    for data in HOTELS.values():
        staff_key, staff_name = data["staff"]
        print(f"  {data['name']}")
        print(f"    {email_for(staff_key, UserRole.HOTEL):<36} {staff_name} (hotel staff)")
        for valet_key, valet_name in data["valets"]:
            print(f"    {email_for(valet_key, UserRole.VALET):<36} {valet_name} (valet)")
    print()
    print(f"{len(HOTELS)} hotels, {len(LOTS)} lots, {len(BOOKINGS)} bookings.")


def main() -> None:
    if "--reset" in sys.argv:
        answer = input(
            "This deletes ALL data in the ParkMate database. Type YES to continue: "
        )
        if answer != "YES":
            print("Cancelled. Nothing was changed.")
            return
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        first_owner = email_for(next(iter(OWNERS)), UserRole.OWNER)
        if db.query(models.User).filter(models.User.email == first_owner).first():
            print("Demo data already exists. Run again with --reset to start fresh.")
            return
        seed(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print_summary()


if __name__ == "__main__":
    main()