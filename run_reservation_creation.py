#!/usr/bin/env python3
"""
DigiStay PMS — Reservation Creation Automation (standalone script).
Run: python run_reservation_creation.py

Automates: Login -> Room View -> Reservations -> Create form -> Mobile -> Add Room modal -> Mandatory fields -> Create.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import BASE_URL, EMAIL, PASSWORD
from src.flows.login_flow import LoginFlow
from src.flows.reservation_flow import ReservationFlow


def load_json(relative_path: str) -> dict:
    with open(PROJECT_ROOT / relative_path, encoding="utf-8") as f:
        return json.load(f)


def main():
    login_data = load_json("data/login_data.json")
    reservation_data = load_json("data/reservation_data.json")
    base_url = login_data.get("base_url", BASE_URL)
    email = login_data.get("email", EMAIL)
    password = login_data.get("password", PASSWORD)
    data = reservation_data["reservation_1"]

    print("[Script] Starting DigiStay reservation creation automation.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(permissions=["camera", "microphone"])
        page = context.new_page()

        try:
            login_flow = LoginFlow(page)
            reservation_flow = ReservationFlow(page)

            print("[Script] Step 1: Login and wait for Room View.")
            login_flow.login_and_land_on_room_view(base_url, email, password)

            print("[Script] Step 2: Create reservation flow.")
            reservation_flow.create_reservation_flow(data, test_name="reservation_creation")

            print("[Script] Reservation creation completed successfully.")
        except Exception as e:
            print(f"[Script] FAILED: {e}")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
