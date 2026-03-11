"""Login Page — DigiStay PMS login and Room View navigation."""
from playwright.sync_api import Page, expect


class LoginPage:
    """Page Object for DigiStay login. Supports both Sign In and Login buttons."""

    def __init__(self, page: Page):
        self.page = page
        self.email_input = (
            page.get_by_placeholder("email", exact=False)
            .or_(page.locator("input[name='email'], input[type='email']"))
            .first
        )
        self.password_input = (
            page.get_by_placeholder("password", exact=False)
            .or_(page.locator("input[name='password'], input[type='password']"))
            .first
        )
        self.login_button = (
            page.get_by_role("button", name="Sign In")
            .or_(page.get_by_role("button", name="Login"))
            .or_(page.locator("button[type='submit']"))
            .first
        )

    def open(self, base_url: str):
        """Open DigiStay PMS login page."""
        self.page.goto(base_url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        print("[Login] Login page opened.")

    def login(self, email: str, password: str):
        """Enter credentials and click Sign In. Waits for Room View after login."""
        expect(self.email_input).to_be_visible(timeout=15000)
        self.email_input.fill(email)
        expect(self.password_input).to_be_visible(timeout=10000)
        self.password_input.fill(password)

        expect(self.login_button).to_be_visible(timeout=10000)
        self.login_button.click()
        print("[Login] Sign In clicked.")