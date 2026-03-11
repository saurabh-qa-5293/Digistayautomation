from playwright.sync_api import Page, expect


class RoomViewPage:
    def __init__(self, page: Page):
        self.page = page
        self.room_view_heading = page.locator("text=Room View").first

        self.start_checkin_option = page.locator("text=/^Start Check-?in$/i").first
        self.checkin_option = page.locator("text=/^Check-?in$/i").first
        # Dropdown menu option — exact match to avoid "Checkout Due" (tile status)
        self.checkout_option = (
            page.locator("[role='menu'] >> text=/^Check-out$/i")
            .or_(page.locator("[role='menu'] >> text=/^Check out$/i"))
            .or_(page.locator("text=/^Check-out$/i"))
            .or_(page.locator("text=/^Check out$/i"))
            .or_(page.locator("text=/^Checkout$/i"))
        ).first
        self.mark_as_clean_option = page.locator("text=Mark as Clean").first

    def wait_for_room_view_to_load(self):
        self.page.wait_for_url("**/room-view**", timeout=30000)
        self.page.wait_for_load_state("networkidle")
        expect(self.room_view_heading).to_be_visible(timeout=15000)

    def get_room_tiles(self):
        self.wait_for_room_view_to_load()

        room_names = [
            "555", "ABCD", "Cow", "Balcony_002", "Balcony_003", "Balcony_005",
            "BV1", "BV2", "BV3", "Digi1", "Digi2", "G1", "G11", "H1", "H11",
            "latest1", "Marvel_001", "Marvel_002", "Planet1", "Planet2", "Planet3",
            "S101", "S102", "S103", "S104", "S105"
        ]

        tiles = []
        for room_name in room_names:
            locator = self.page.locator(f"text={room_name}").first
            if locator.count() > 0:
                try:
                    if locator.is_visible():
                        tiles.append(locator)
                except Exception:
                    pass

        return tiles

    def close_open_popup_if_any(self):
        """Press Escape to close any open dropdown/modal, then ensure the overlay is gone."""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        self._force_dismiss_overlay()

    def _force_dismiss_overlay(self, timeout_ms: int = 3000):
        """If a fixed overlay is still blocking the page, dismiss it by any means necessary."""
        overlay_sel = "div.fixed.inset-0"
        try:
            overlay = self.page.locator(overlay_sel).first
            if overlay.count() == 0 or not overlay.is_visible():
                return  # already gone

            # 1. Try pressing Escape once more
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(400)

            # 2. If still visible, force-click the overlay itself to dismiss it
            if overlay.count() > 0 and overlay.is_visible():
                overlay.click(force=True)
                self.page.wait_for_timeout(400)

            # 3. If still visible, click a safe neutral point (top-left corner of page)
            if overlay.count() > 0 and overlay.is_visible():
                self.page.mouse.click(5, 5)
                self.page.wait_for_timeout(400)

            # 4. Final wait for overlay to be hidden
            try:
                overlay.wait_for(state="hidden", timeout=timeout_ms)
            except Exception:
                pass
        except Exception:
            pass

    def start_checkin_from_first_available_tile(self) -> bool:
        self.wait_for_room_view_to_load()
        tiles = self.get_room_tiles()

        if not tiles:
            raise Exception("No actual room tiles found on Room View page.")

        for index, tile in enumerate(tiles):
            try:
                self.close_open_popup_if_any()

                tile_text = tile.inner_text().strip()
                print(f"Trying room tile {index + 1}: {tile_text}")

                tile.click(timeout=5000)
                self.page.wait_for_timeout(1000)

                # 1. Look for Start Check-in in dropdown first
                if self.start_checkin_option.count() > 0 and self.start_checkin_option.is_visible():
                    print(f"Start Check-in found for room: {tile_text}")
                    self.start_checkin_option.click()
                    self.page.wait_for_timeout(1500)
                    return True

                # 2. If no Start Check-in, look for Check-in in dropdown
                if self.checkin_option.count() > 0 and self.checkin_option.is_visible():
                    print(f"Check-in found for room: {tile_text}")
                    self.checkin_option.click()
                    self.page.wait_for_timeout(1500)
                    return True

                # 3. No check-in option on this tile -> close dropdown and try next tile
                if self.checkout_option.count() > 0 and self.checkout_option.is_visible():
                    print(f"Check-out only for room: {tile_text} -> switching to next tile")
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(300)
                    self._force_dismiss_overlay()
                    continue

                if self.mark_as_clean_option.count() > 0 and self.mark_as_clean_option.is_visible():
                    print(f"No check-in action for room: {tile_text} -> switching to next tile")
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(300)
                    self._force_dismiss_overlay()
                    continue

                print(f"No check-in option for room: {tile_text} -> switching to next tile")
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
                self._force_dismiss_overlay()

            except Exception as e:
                print(f"Could not use room tile {index + 1}: {e}")
                try:
                    self._force_dismiss_overlay()
                except Exception:
                    pass
                # If page/context/browser was closed (e.g. by timeout), stop iterating
                try:
                    if not self.page.context.pages or not self.page.context.browser or not self.page.context.browser.is_connected():
                        break
                except Exception:
                    break
                continue

        # No tile had Start check-in or Check-in -> close browser
        print("No tile with Start check-in or Check-in found. Closing browser.")
        if self.page.context.browser:
            self.page.context.browser.close()
        return False

    def start_checkout_from_first_checked_in_tile(self) -> bool:
        """Click the first room tile that shows a 'Check out' option and select it.

        Returns True if a Check-out action was started, False if no tile was found.
        Closes the browser if no tile has a Check-out option.
        """
        self.wait_for_room_view_to_load()
        tiles = self.get_room_tiles()

        if not tiles:
            raise Exception("No room tiles found on Room View page.")

        for index, tile in enumerate(tiles):
            try:
                self.close_open_popup_if_any()

                tile_text = tile.inner_text().strip()
                print(f"[Checkout] Trying room tile {index + 1}: {tile_text}")

                tile.click(timeout=5000)
                self.page.wait_for_timeout(1200)

                # Look for "Check out" dropdown option (exact match — not "Checkout Due")
                if self.checkout_option.count() > 0 and self.checkout_option.is_visible():
                    print(f"[Checkout] 'Check out' option found for room: {tile_text}")
                    self.checkout_option.scroll_into_view_if_needed()
                    self.checkout_option.click(timeout=8000)
                    self.page.wait_for_timeout(1500)
                    return True

                print(f"[Checkout] No 'Check out' option for room: {tile_text} → switching to next tile")
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
                self._force_dismiss_overlay()

            except Exception as e:
                print(f"[Checkout] Could not use room tile {index + 1}: {e}")
                try:
                    self._force_dismiss_overlay()
                except Exception:
                    pass
                try:
                    if not self.page.context.pages or not self.page.context.browser or not self.page.context.browser.is_connected():
                        break
                except Exception:
                    break
                continue

        print("[Checkout] No tile with Check-out option found.")
        return False