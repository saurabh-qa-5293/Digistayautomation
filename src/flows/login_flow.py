from src.pages.login_page import LoginPage
from src.pages.room_view_page import RoomViewPage


class LoginFlow:
    def __init__(self, page):
        self.page = page
        self.login_page = LoginPage(page)
        self.room_view_page = RoomViewPage(page)

    def login_and_land_on_room_view(self, base_url: str, email: str, password: str):
        self.login_page.open(base_url)
        self.login_page.login(email, password)
        self.room_view_page.wait_for_room_view_to_load()