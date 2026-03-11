from playwright.sync_api import Page
from locators.room_type_ids import RoomTypeIDs

class room_type_page:

    def __init__(self, page: Page):
        self.page = page

    def open_create_roomtype(self):
        self.page.get_by_test_id(RoomTypeIDs.CREATE_BTN).click()

    def enter_roomtype_name(self, name):
        self.page.get_by_test_id(RoomTypeIDs.NAME).fill(name)

    def set_occupancy(self, base_adults, max_adults):
        self.page.get_by_test_id(RoomTypeIDs.BASE_ADULTS).fill(str(base_adults))
        self.page.get_by_test_id(RoomTypeIDs.MAX_ADULTS).fill(str(max_adults))

    def set_pricing(self, base_price):
        self.page.get_by_test_id(RoomTypeIDs.BASE_PRICE).fill(str(base_price))

    def save_roomtype(self):
        self.page.get_by_test_id(RoomTypeIDs.SAVE).click()