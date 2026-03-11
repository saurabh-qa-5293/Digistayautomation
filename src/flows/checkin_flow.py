from pathlib import Path

from src.pages.room_view_page import RoomViewPage
from src.pages.checkin_page import CheckinPage


class CheckinFlow:
    def __init__(self, page):
        self.page = page
        self.room_view_page = RoomViewPage(page)
        self.checkin_page = CheckinPage(page)

    def start_checkin_from_room_view(self):
        self.room_view_page.wait_for_room_view_to_load()

        started = self.room_view_page.start_checkin_from_first_available_tile()
        if not started:
            raise Exception("No room tile found with Check-in or Start Check-in action.")

    def complete_checkin_flow(self, guest_data: dict):
        """Complete the check-in flow: ID step, basic details, then complete check-in."""
        self.checkin_page.wait_for_checkin_flow_to_open()
        self.checkin_page.select_indian_if_available()

        # __file__ is src/flows/checkin_flow.py → parents[2] = project root
        project_root = Path(__file__).resolve().parents[2]

        # Always click "Add ID" to open the upload UI, regardless of file availability
        self.checkin_page.click_add_id_and_open_upload_ui()

        front_path = guest_data.get("document_file_front")
        back_path = guest_data.get("document_file_back")
        if front_path and back_path:
            full_front = str(project_root / front_path)
            full_back = str(project_root / back_path)
            if Path(full_front).exists() and Path(full_back).exists():
                try:
                    self.checkin_page.set_front_and_back_id_files(full_front, full_back)
                except Exception as e:
                    print(f"ID upload failed: {e}")
            else:
                print(
                    f"ID files not found — skipping upload.\n"
                    f"  Front: {full_front}\n"
                    f"  Back : {full_back}\n"
                    "Add these files to data/ so the Next button becomes enabled."
                )
        else:
            document_file = guest_data.get("document_file")
            if document_file:
                full_path = str(project_root / document_file)
                if Path(full_path).exists():
                    try:
                        self.checkin_page.set_single_id_file(full_path)
                    except Exception as e:
                        print(f"ID upload failed: {e}")
        self.checkin_page.click_primary_next()

        self.checkin_page.wait_for_basic_details_screen()
        self.checkin_page.fill_basic_details(guest_data)

        # Basic Details screen has a "CHECK IN" button — click it directly
        self.checkin_page.complete_checkin()
        self.checkin_page.verify_checkin_success()

        # After CHECK IN is clicked the app redirects to checkin-details / viewGuestInfo.
        # Hold briefly so the redirect completes before the next step runs.
        self._wait_for_checkin_details_redirect()

    def _wait_for_checkin_details_redirect(self, timeout_ms: int = 15000):
        """Wait until the browser leaves the new-check-in page and lands on checkin details."""
        try:
            self.page.wait_for_url(
                lambda url: "new-check-in" not in url,
                timeout=timeout_ms,
            )
            self.page.wait_for_load_state("networkidle")
            print(f"[Check-in] Redirected to: {self.page.url}")
        except Exception:
            print(f"[Check-in] Still on: {self.page.url} after waiting — continuing anyway.")