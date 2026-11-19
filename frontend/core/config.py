import os

API_URL = os.getenv("PARKMATE_API_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 10

ROLE_LABELS = {
    "owner": "Parking lot owner",
    "hotel": "Hotel staff",
    "valet": "Valet",
}