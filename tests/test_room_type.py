from pages.room_type_page import room_type_page
import pytest

@pytest.mark.skip(reason="Room type is part of settings, skipping for now")
def test_create_roomtype(page):

    roomtype = room_type_page(page)

    page.goto("https://stage-hotel.digistays.com/roomtype")

    roomtype.open_create_roomtype()

    roomtype.enter_roomtype_name("Automation Deluxe")

    roomtype.set_occupancy(2,3)

    roomtype.set_pricing(2500)

    roomtype.save_roomtype()
    roomtype = RoomTypePage(page)

    page.goto("https://stage-hotel.digistays.com/login")
    page.wait_for_timeout(3000)  # only for debugging,
    # do login here

    page.goto("https://stage-hotel.digistays.com/roomview")