"""
Reservation Flow — DigiStay PMS Create Reservation automation.
Orchestrates: Login -> Reservations -> Form -> Mobile -> Add Room modal -> Mandatory fields -> Create.
Uses try/except, screenshots on failure, clear error messages.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

from src.pages.reservations_page import ReservationsPage
from utils.screenshot_utils import take_failure_screenshot


class ReservationFlow:
    """Orchestrates the full Create Reservation flow per specification."""

    def __init__(self, page):
        self.page = page
        self.reservations_page = ReservationsPage(page)

    @staticmethod
    def _build_date(days_from_today: int) -> str:
        return (datetime.today() + timedelta(days=days_from_today)).strftime("%d/%m/%Y")

    @staticmethod
    def _load_guest_data(key: str = "valid_guest_1") -> dict:
        project_root = Path(__file__).resolve().parents[2]
        with open(project_root / "data" / "guest_data.json", encoding="utf-8") as f:
            return json.load(f)[key]

    def create_reservation_flow(self, data: dict, guest_key: str = "valid_guest_1", test_name: str = "create_reservation"):
        """
        Flow: Reservations -> Form -> Mobile -> Add Room modal -> Mandatory fields -> Create.
        """
        guest = self._load_guest_data(guest_key)
        full_name = f"{guest['first_name']} {guest['last_name']}"
        mobile = guest["mobile"]
        email = guest.get("email", "guest@test.com")

        room_count = data.get("number_of_rooms", 1)
        room_names = data.get("rooms") or ["BV1"] * room_count
        if isinstance(room_names, list):
            room_names = room_names[:room_count] if len(room_names) >= room_count else room_names + ["BV1"] * (room_count - len(room_names))
        else:
            room_names = ["BV1"] * room_count

        checkin_date = self._build_date(data.get("checkin_days_from_today", 1))
        checkout_date = self._build_date(data.get("checkout_days_from_today", 3))
        form_data = {**data, "checkin_date": checkin_date, "checkout_date": checkout_date}

        print("[Flow] Step 1: Navigate to Reservations and open form.")
        self.reservations_page.go_to_reservations()
        self.reservations_page.open_reservation_form_and_wait_for_load()
        self.reservations_page.wait_for_reservation_page_ready()

        print("[Flow] Step 2: Fill mobile number.")
        self.reservations_page.fill_mobile_number(mobile)

        print("[Flow] Step 3: Open Add Room modal and select room(s).")
        try:
            self.reservations_page.click_add_room_and_wait_for_modal()
            for rn in room_names:
                self.reservations_page.select_room_from_modal(rn)
            self.reservations_page.click_modal_add_room_and_wait_for_close()
            self.reservations_page.verify_rooms_added_to_form(len(room_names))
        except RuntimeError as e:
            if any(msg in str(e) for msg in ["Target room not found", "Plus button not found", "Add Room footer button not found"]):
                take_failure_screenshot(self.page, f"{test_name}_add_room_modal_fail")
            raise

        print("[Flow] Step 4: Fill mandatory fields (guest name, email, source, dates, guests).")
        self.reservations_page.fill_guest_name(full_name)
        if email:
            self.reservations_page.add_email_if_needed_and_fill(email)
        self.reservations_page.fill_mandatory_fields_dynamic(form_data)

        print("[Flow] Step 5: Create reservation.")
        try:
            self.reservations_page.submit_create_reservation_and_wait_for_detail()
        except Exception as e:
            take_failure_screenshot(self.page, f"{test_name}_create_btn_fail")
            missing = self.reservations_page._suggest_missing_mandatory_field()
            if missing:
                print(f"[Flow] Create Reservation may be disabled. Possible missing field: {missing}")
            raise

        print("[Flow] Step 6: Validate reservation detail page.")
        assert self.reservations_page.validate_reservation_detail(), "Reservation detail page not validated."
        path = take_failure_screenshot(self.page, f"{test_name}_success")
        print(f"[Flow] Screenshot saved: {path}")
