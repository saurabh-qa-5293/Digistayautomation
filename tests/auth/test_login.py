from config.settings import BASE_URL, EMAIL, PASSWORD
from src.flows.login_flow import LoginFlow
from src.pages.login_page import LoginPage


LOGIN_DATA = {
    "base_url": BASE_URL,
    "email": EMAIL,
    "password": PASSWORD
}


class TestLogin:

    def test_login_page_loads(self, page):
        login_page = LoginPage(page)
        login_page.open(LOGIN_DATA["base_url"])
        login_page.verify_login_page_loaded()

    def test_login_with_valid_credentials(self, page):
        login_flow = LoginFlow(page)
        login_flow.login_and_land_on_home(
            LOGIN_DATA["base_url"],
            LOGIN_DATA["email"],
            LOGIN_DATA["password"]
        )