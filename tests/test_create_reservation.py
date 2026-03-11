import json
from pathlib import Path

import pytest

from src.flows.login_flow import LoginFlow
from src.flows.reservation_flow import ReservationFlow


# ── Helper ────────────────────────────────────────────────────────────────────

def load_json(relative_path: str) -> dict:
    project_root = Path(__file__).resolve().parents[1]
    with open(project_root / relative_path, encoding="utf-8") as f:
        return json.load(f)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCreateReservation:
    """Test suite for the DigiStay PMS Reservation creation flow."""

    def test_create_reservation(self, page):
        """
        End-to-end: Login -> Room View -> Reservations -> Form -> Mobile -> Add Room modal -> Mandatory fields -> Create.
        Validates reservation detail page and takes screenshot.
        """
        login_data = load_json("data/login_data.json")
        reservation_data = load_json("data/reservation_data.json")
        data = reservation_data["reservation_1"]

        login_flow = LoginFlow(page)
        reservation_flow = ReservationFlow(page)

        login_flow.login_and_land_on_room_view(
            login_data["base_url"],
            login_data["email"],
            login_data["password"],
        )
        print("URL after login:", page.url)

        reservation_flow.create_reservation_flow(data, test_name="test_create_reservation")
        print("Reservation creation flow completed successfully.")

    @pytest.mark.parametrize("reservation_key", ["reservation_1", "reservation_2"])
    def test_create_multiple_reservations(self, page, reservation_key):
        """Parametrized test — creates each reservation defined in reservation_data.json."""
        login_data = load_json("data/login_data.json")
        reservation_data = load_json("data/reservation_data.json")
        data = reservation_data[reservation_key]

        login_flow = LoginFlow(page)
        reservation_flow = ReservationFlow(page)

        login_flow.login_and_land_on_room_view(
            login_data["base_url"],
            login_data["email"],
            login_data["password"],
        )

        reservation_flow.create_reservation_flow(data)
        print(f"Reservation '{reservation_key}' created successfully.")
