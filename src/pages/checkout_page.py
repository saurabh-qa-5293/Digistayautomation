from playwright.sync_api import Page, expect


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

        # Checkout screen — "Early Check-out" button (top-right, purple)
        self.early_checkout_btn = (
            page.locator("button:has-text('Early Check-out')")
            .or_(page.locator("button:has-text('Early Checkout')"))
            .or_(page.locator("button:has-text('Early Check Out')"))
            .first
        )

        # Confirmation modal — "Checkout Anyway" button
        self.checkout_anyway_btn = (
            page.locator("button:has-text('Checkout Anyway')")
            .or_(page.locator("button:has-text('Check out Anyway')"))
            .or_(page.locator("button:has-text('Checkout anyway')"))
            .first
        )

        # Confirmation modal — "Settle Payment" button (alternative path, not taken here)
        self.settle_payment_btn = page.locator("button:has-text('Settle Payment')").first

        # Success/completion indicator after checkout
        self.checkout_success = (
            page.locator("text=/checked.?out.?successfully/i")
            .or_(page.locator("text=/checkout.*success/i"))
            .or_(page.locator("text=/successfully.*checked.?out/i"))
        )

    def wait_for_checkout_screen(self):
        """Wait until the Checkout / Check-in Details screen loads."""
        self.page.wait_for_url("**/checkout**", timeout=20000)
        self.page.wait_for_load_state("networkidle")
        print("[Checkout] Checkout screen loaded.")

    def wait_for_checkout_screen_by_content(self):
        """Fallback: wait for Early Check-out button to be visible (URL-independent)."""
        expect(self.early_checkout_btn).to_be_visible(timeout=20000)
        print("[Checkout] Early Check-out button visible on screen.")

    def click_early_checkout(self):
        """Click the 'Early Check-out' button on the checkout screen."""
        expect(self.early_checkout_btn).to_be_visible(timeout=15000)
        self.early_checkout_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)
        print("[Checkout] Clicking Early Check-out button...")
        self.early_checkout_btn.click()
        self.page.wait_for_timeout(1000)

    def click_checkout_anyway(self):
        """Click 'Checkout Anyway' in the 'Please confirm' modal."""
        expect(self.checkout_anyway_btn).to_be_visible(timeout=10000)
        self.checkout_anyway_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(300)
        print("[Checkout] Clicking 'Checkout Anyway' in confirm modal...")
        self.checkout_anyway_btn.click()
        self.page.wait_for_timeout(1500)

    def verify_checkout_success(self):
        """Verify checkout completed — either by success message or URL change."""
        try:
            expect(self.checkout_success).to_be_visible(timeout=15000)
            print("[Checkout] Success message visible — checkout completed.")
        except Exception:
            current_url = self.page.url
            if "checkout" not in current_url.lower() or "room-view" in current_url.lower():
                print(f"[Checkout] Page navigated away from checkout → {current_url} — treating as success.")
            else:
                raise
