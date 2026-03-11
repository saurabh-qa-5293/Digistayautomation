class ReservationPage:
    def __init__(self, page):
        self.page = page

    def open_create_reservation(self):
        self.page.get_by_test_id("reservation__create_btn").click()

    def fill_basic_details(self, data):
        self.page.get_by_test_id("reservation__checkin_date__input").fill(data["checkin_date"])
        self.page.get_by_test_id("reservation__checkout_date__input").fill(data["checkout_date"])
        self.page.get_by_test_id("reservation__room_count__input").fill(str(data["room_count"]))
        self.page.get_by_test_id("reservation__continue__btn").click()

    def fill_reservation_details(self, data):
        self.page.get_by_test_id("reservation__guest_name__input").fill(data["guest_name"])
        self.page.get_by_test_id("reservation__mobile__input").fill(data["mobile"])
        self.page.get_by_test_id("reservation__email__input").fill(data["email"])
        self.page.get_by_test_id("reservation__save__btn").click()

    def start_checkin(self):
        self.page.get_by_test_id("reservation__start_checkin__btn").click()