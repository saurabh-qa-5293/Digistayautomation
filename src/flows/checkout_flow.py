from src.pages.room_view_page import RoomViewPage
from src.pages.checkout_page import CheckoutPage


class CheckoutFlow:
    def __init__(self, page):
        self.page = page
        self.room_view_page = RoomViewPage(page)
        self.checkout_page = CheckoutPage(page)

    def navigate_to_room_view(self):
        """Go back to Room View using the sidebar link."""
        try:
            room_view_link = self.page.locator("text=Room view, text=Room View").first
            if room_view_link.count() == 0:
                room_view_link = self.page.get_by_role("link", name="Room view").first
            if room_view_link.count() > 0 and room_view_link.is_visible():
                room_view_link.click()
                self.page.wait_for_timeout(1500)
                print("[Checkout] Navigated to Room View via sidebar.")
                return
        except Exception:
            pass

        # Fallback: navigate directly via URL
        current_url = self.page.url
        if "/hotels/" in current_url:
            hotel_segment = current_url.split("/hotels/")[1].split("/")[0]
            room_view_url = f"{current_url.split('/hotels/')[0]}/hotels/{hotel_segment}/room-view"
            print(f"[Checkout] Navigating directly to Room View: {room_view_url}")
            self.page.goto(room_view_url)
            self.page.wait_for_timeout(1500)

    def start_checkout_from_room_view(self):
        """Go to Room View, find a checked-in room tile, and click 'Check out'."""
        self.room_view_page.wait_for_room_view_to_load()

        started = self.room_view_page.start_checkout_from_first_checked_in_tile()
        if not started:
            raise Exception("No room tile found with 'Check out' option.")

    def complete_checkout(self):
        """On the Checkout screen: click Early Check-out → confirm modal → Checkout Anyway."""
        # Wait for the checkout screen to load (try URL-based, then content-based)
        try:
            self.checkout_page.wait_for_checkout_screen()
        except Exception:
            print("[Checkout] URL-based wait timed out, trying content-based wait...")
            self.checkout_page.wait_for_checkout_screen_by_content()

        self.checkout_page.click_early_checkout()
        self.checkout_page.click_checkout_anyway()
        self.checkout_page.verify_checkout_success()
