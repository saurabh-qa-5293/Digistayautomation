import json
from pathlib import Path
from pages.room_view_page import RoomViewPage
from pages.checkin_page import CheckinPage


def load_guest_data():
    data_path = Path(__file__).resolve().parents[2] / "data" / "guest_data.json"
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)


def test_create_checkin_from_room_view(page, login_to_app):
    room_view_page = RoomViewPage(page)
    checkin_page = CheckinPage(page)

    guest_data = load_guest_data()["primary_guest"]

    test_data_dir = Path(__file__).resolve().parents[2] / "test_data"
    guest_id_front = test_data_dir / "guest_id_front.png"

    room_view_page.open_room_view()

    started = room_view_page.find_and_start_checkin(hold_time=2)
    assert started, "No room tile with Start Check-in option was found"

    checkin_page.fill_guest_details(guest_data)
    checkin_page.upload_guest_document(guest_id_front)
    checkin_page.continue_flow()

    # add further steps here when updated flow fields are added

    checkin_page.complete_checkin()
    assert checkin_page.is_success_visible(), "Check-in success message not visible"