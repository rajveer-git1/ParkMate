# ParkMate Database Design

## Table 1: users
Everyone who can log in: owners, hotel staff, valets.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Required |
| email | String(120) | Required, unique (used to log in) |
| phone | String(20) | Optional |
| password_hash | String(255) | Required. Never store the real password |
| role | String(20) | "owner", "hotel", or "valet" |
| hotel_id | Integer | Foreign key -> hotels.id. Empty for owners |
| is_active | Boolean | Default True |
| created_at | DateTime | Set automatically |

## Table 2: hotels
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Required |
| address | String(255) | Required |
| city | String(100) | Required |
| latitude | Float | Used for nearby-lot search |
| longitude | Float | Used for nearby-lot search |
| created_at | DateTime | Set automatically |

## Table 3: parking_lots
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| owner_id | Integer | Foreign key -> users.id (the owner) |
| name | String(100) | Required |
| address | String(255) | Required |
| city | String(100) | Required |
| latitude | Float | Used for nearby-lot search |
| longitude | Float | Used for nearby-lot search |
| total_slots | Integer | Maximum cars the lot can hold |
| price_per_hour | Float | Parking rate |
| is_active | Boolean | Default True |
| created_at | DateTime | Set automatically |

## Table 4: bookings
One row = one car parked by a valet.

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| hotel_id | Integer | Foreign key -> hotels.id |
| lot_id | Integer | Foreign key -> parking_lots.id |
| valet_id | Integer | Foreign key -> users.id (valet who checked in) |
| guest_name | String(100) | Required |
| guest_phone | String(20) | Required |
| vehicle_number | String(20) | Required |
| vehicle_model | String(50) | Optional |
| price_per_hour | Float | Copied from the lot at check-in |
| check_in_time | DateTime | Set at check-in |
| check_out_time | DateTime | Empty until the car is returned |
| total_fee | Float | Empty until checkout |
| status | String(20) | "parked" or "completed" |

## Relationships
- One owner (user) has many parking lots
- One hotel has many users (staff and valets)
- One hotel has many bookings
- One parking lot has many bookings
- One valet (user) has many bookings

## Business rules (calculated in code, not stored)
- Lot is **Full** when the number of "parked" bookings in it >= total_slots, otherwise **Available**
- Fee = hours parked (rounded up, minimum 1 hour) x price_per_hour
- Nearby lots = lots sorted by distance from the hotel's latitude/longitude