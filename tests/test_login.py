# tests/test_login.py
from src.flows.login_flow import LoginFlow
from config.setting import BASE_URL, EMAIL, PASSWORD

def test_login(page):
    login_flow = LoginFlow(page)
    login_flow.login_and_land_on_room_view(BASE_URL, EMAIL, PASSWORD)