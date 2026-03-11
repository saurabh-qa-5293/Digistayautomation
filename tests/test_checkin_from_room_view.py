import json
from pathlib import Path

from src.flows.login_flow import LoginFlow
from src.flows.checkin_flow import CheckinFlow
from src.flows.checkout_flow import CheckoutFlow


def load_json_data(file_path: str):
    project_root = Path(__file__).resolve().parents[1]
    full_path = project_root / file_path

    with open(full_path, "r", encoding="utf-8") as file:
        return json.load(file)


class TestCheckinFromRoomView:
    def test_checkin_from_room_view(self, page):
        login_data = load_json_data("data/login_data.json")
        all_guest_data = load_json_data("data/guest_data.json")
        guest_data = all_guest_data["valid_guest_1"]

        login_flow = LoginFlow(page)
        checkin_flow = CheckinFlow(page)
        checkout_flow = CheckoutFlow(page)

        # ── Step 1: Login and land on Room View ──
        login_flow.login_and_land_on_room_view(
            login_data["base_url"],
            login_data["email"],
            login_data["password"]
        )
        print("URL after login:", page.url)

        # ── Step 2: Find a room with 'Start Check-in' and begin check-in ──
        checkin_flow.start_checkin_from_room_view()
        print("URL after clicking room tile:", page.url)
        assert "food" not in page.url.lower(), f"Wrong navigation happened: {page.url}"

        # ── Step 3: Complete the full check-in flow ──
        # (ID upload → Basic Details → CHECK IN → wait for checkin-details redirect)
        checkin_flow.complete_checkin_flow(guest_data)
        print("URL after check-in completed:", page.url)

        # ── Step 4: Navigate back to Room View ──
        checkout_flow.navigate_to_room_view()
        print("URL after navigating to Room View:", page.url)

        # ── Step 5: Find the checked-in room tile and click 'Check out' ──
        checkout_flow.start_checkout_from_room_view()
        print("URL after clicking Check out:", page.url)

        # ── Step 6: Early Check-out → Checkout Anyway ──
        checkout_flow.complete_checkout()
        print("Checkout flow completed successfully.")