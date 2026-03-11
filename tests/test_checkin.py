import pytest
import os
from src.flows.login_flow import LoginFlow
from src.flows.reservation_flow import ReservationFlow
from src.flows.checkin_flow import CheckinFlow
from config.setting import BASE_URL, EMAIL, PASSWORD

def test_checkin_flow(page):
    login_flow = LoginFlow(page)
    reservation_flow = ReservationFlow(page)
    checkin_flow = CheckinFlow(page)

    # 1. Login
    login_flow.login_and_land_on_room_view(BASE_URL, EMAIL, PASSWORD)

    # 2. Create Reservation
    reservation_basic = {
        "checkin_date": "2026-03-07",
        "checkout_date": "2026-03-08",
        "room_count": 1
    }
    reservation_details = {
        "guest_name": "Test User",
        "mobile": "9999999999",
        "email": "test@test.com"
    }

    reservation_flow.create_reservation(reservation_basic, reservation_details)

    # Click on the start checkin button
    reservation_flow.reservation_page.start_checkin()

    # 3. Complete checkin
    guest = {
        "first_name": "Rahul",
        "last_name": "Sharma",
        "mobile": "9876543210",
        "email": "rahul.sharma@test.com"
    }
    basic = {
        "nationality": "Indian",
        "address": "Delhi, India"
    }
    details = {
        "adults": 1,
        "children": 0
    }
    
    # Path to document file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    id_file = os.path.join(base_dir, "testdata", "documents", "Adhar_ FRont.png")

    checkin_flow.complete_checkin(guest, basic, details, id_file)
    
    # Give some time to visually confirm or process checkin completion
    page.wait_for_timeout(2000)
