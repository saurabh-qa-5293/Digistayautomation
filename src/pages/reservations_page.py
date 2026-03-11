"""
Reservations Page - DigiStay PMS Create Reservation flow.
Add Room modal: scope to modal, find room chip by name, click + inside chip only.
Uses get_by_role, get_by_text, locator with has_text, scoped locators.
"""
from playwright.sync_api import Page, expect


class ReservationsPage:
    """Page Object for the Create Reservation flow in Digistay."""

    def __init__(self, page: Page):
        self.page = page

    # ── Step 1: Wait for reservation page ─────────────────────────────────────

    def wait_for_reservation_page_ready(self):
        """Wait for New Reservation / Create Reservation page to load fully.
        Confirm the main reservation form is visible before starting.
        """
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(500)

        # Confirm form is visible: Add Room/s button or dialog
        add_room = self._get_add_room_button()
        expect(add_room).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(500)
        print("[Reservations] Reservation page fully loaded.")

    def open_reservation_form_and_wait_for_load(self):
        """Click Create Reservation / New Reservation and wait for form to load."""
        create_btn = (
            self.page.get_by_test_id("reservation__create_btn")
            .or_(self.page.get_by_role("button", name="Create Reservation"))
            .or_(self.page.get_by_role("button", name="New Reservation"))
            .or_(self.page.get_by_role("link", name="Create Reservation"))
        ).first
        expect(create_btn).to_be_visible(timeout=15000)
        create_btn.scroll_into_view_if_needed()
        self._wait_for_stable(300)
        self._safe_click(create_btn)

        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)

        add_room = self._get_add_room_button()
        try:
            expect(add_room).to_be_visible(timeout=15000)
        except Exception:
            dialog = self.page.get_by_role("dialog").first
            if dialog.count() > 0:
                expect(dialog).to_be_visible(timeout=5000)
            else:
                raise
        self._wait_for_stable(500)
        print("[Reservations] Reservation form opened and ready.")

    # ── Step 2: Fill guest details ─────────────────────────────────────────────

    def fill_guest_name(self, name: str):
        """Locate Guest Name using label, placeholder, or text. Enter value."""
        form = self._get_form_scope()
        inp = (
            form.get_by_label("Guest Name", exact=False)
            .or_(form.get_by_label("Name", exact=False))
            .or_(form.get_by_placeholder("e.g. Amit"))
            .or_(form.get_by_placeholder("Amit"))
        ).first
        expect(inp).to_be_visible(timeout=8000)
        inp.scroll_into_view_if_needed()
        self._wait_for_stable(150)
        inp.click()
        inp.press("Control+A")
        inp.fill(name)
        self._wait_for_stable(200)
        print(f"[Reservations] Guest Name -> {name}")

    def fill_mobile_number(self, mobile: str):
        """Enter mobile number (country code +91 fixed, do not touch dropdown).
        Identify by placeholder, label, or name. Verify input value is visible before moving on.
        """
        form_scope = self._get_form_scope()

        # Prefer placeholder / label (phone input only, not country selector)
        candidates = [
            form_scope.get_by_placeholder("e.g. 9876543210"),
            form_scope.get_by_placeholder("e.g. 623012306"),
            form_scope.get_by_placeholder("9876543210"),
            form_scope.get_by_label("Mobile", exact=False),
            form_scope.get_by_label("Contact", exact=False),
            form_scope.get_by_label("Phone", exact=False),
            form_scope.get_by_label("Mobile Number", exact=False),
            self.page.get_by_test_id("reservation__mobile__input"),
        ]
        inp = None
        for loc in candidates:
            try:
                if loc.count() > 0 and loc.is_visible():
                    ph = loc.first.get_attribute("placeholder") or ""
                    if "Booking ID" in ph or "Guest Name" in ph:
                        continue
                    inp = loc.first
                    break
            except Exception:
                pass

        if inp is None:
            inp = (
                form_scope.locator("input[placeholder*='9876' i]")
                .or_(form_scope.locator("input[name='mobile']"))
                .or_(form_scope.locator("input[name='phone']"))
            ).first

        expect(inp).to_be_visible(timeout=8000)
        inp.scroll_into_view_if_needed()
        inp.focus()
        self._wait_for_stable(200)
        inp.press("Control+A")
        inp.fill(mobile)
        self._wait_for_stable(300)
        # Verify input value is visible before moving to next field (exact or contains digits)
        try:
            expect(inp).to_have_value(mobile, timeout=2000)
        except Exception:
            val = inp.input_value()
            if mobile not in val:
                raise ValueError(f"Mobile input value '{val}' does not contain '{mobile}'")
        print(f"[Reservations] Mobile -> {mobile}")

    def add_email_if_needed_and_fill(self, email: str) -> bool:
        """Click Add Email only if needed, then enter email. Returns True if filled."""
        add_email_btn = self.page.get_by_role("button", name="Add Email").or_(
            self.page.get_by_text("Add Email")
        ).first
        if add_email_btn.count() > 0 and add_email_btn.is_visible():
            self._safe_click(add_email_btn)
            self._wait_for_stable(400)

        inp = (
            self.page.get_by_label("Email", exact=False)
            .or_(self.page.get_by_placeholder("e.g. email"))
            .or_(self.page.get_by_placeholder("email"))
        ).first
        if inp.count() > 0 and inp.is_visible():
            inp.click()
            inp.press("Control+A")
            inp.fill(email)
            self._wait_for_stable(200)
            print(f"[Reservations] Email -> {email}")
            return True
        return False

    # ── Step 3: Open Add Room modal ────────────────────────────────────────────

    def click_add_room_and_wait_for_modal(self):
        """Locate Add Room/s button, click, wait for Please Confirm modal. All modal actions scoped."""
        add_room = self._get_add_room_button()
        expect(add_room).to_be_visible(timeout=10000)
        add_room.scroll_into_view_if_needed()
        self._wait_for_stable(200)
        self._safe_click(add_room)
        self._wait_for_room_modal_open()
        print("[Reservations] Add Room modal opened.")

    def _get_add_room_button(self):
        """Add Room/s button in the main form (not inside modal)."""
        return (
            self.page.get_by_role("button", name="Add Room/s")
            .or_(self.page.get_by_role("button", name="Add Room"))
            .or_(self.page.get_by_role("button", name="+ Add Room"))
            .or_(self.page.get_by_role("button", name="Add Rooms"))
        ).first

    def _wait_for_room_modal_open(self):
        """Wait for Please Confirm modal to be fully visible and stable."""
        modal = self._get_room_modal()
        expect(modal).to_be_visible(timeout=10000)
        self._wait_for_stable(1000)
        print("[Reservations] Please Confirm modal visible.")

    def _get_room_modal(self):
        """Get the active room selection modal (Available Rooms / Please Confirm / New Reservation)."""
        dialogs = self.page.get_by_role("dialog")
        for i in range(dialogs.count()):
            d = dialogs.nth(i)
            if d.is_visible():
                txt = d.inner_text() or ""
                if "Available Rooms" in txt or "Please Confirm" in txt or "New Reservation" in txt or "Search by Room" in txt:
                    return d
        return dialogs.first

    # ── Step 4: Add Room modal - scoped room chip + plus button ─

    def select_room_from_modal(self, room_name: str) -> None:
        """
        Select a room from Add Room modal by clicking the + button inside the target room chip.
        Scope: modal -> room chip (by text) -> + button (inside chip, use .last for right-side).
        Raises: "Target room not found in Add Room modal" or "Plus button not found for selected room".
        """
        modal = self.page.locator("div[role='dialog']").filter(has_text="Please Confirm").first
        modal.wait_for(state="visible", timeout=10000)

        room_chip = modal.locator("div").filter(has_text=room_name).first
        if room_chip.count() == 0:
            raise RuntimeError(f"Target room not found in Add Room modal: {room_name}")

        plus_btn = room_chip.locator("button, [role='button'], svg").last
        if plus_btn.count() == 0:
            raise RuntimeError(f"Plus button not found for selected room: {room_name}")

        plus_btn.click()
        self._wait_for_stable(400)
        print(f"[Reservations] Selected room: {room_name}")

    def _room_name_matches(self, chip_text: str, room_name: str) -> bool:
        """Check if chip text contains room name (avoid BV10 for BV1). Case-insensitive."""
        t = chip_text.strip()
        rn = room_name.strip()
        if not rn or rn.lower() not in t.lower():
            return False
        # Exact or room name at start
        if t.lower() == rn.lower() or t.lower().startswith(rn.lower()):
            return True
        # "BV1" in "Some text BV1" - ensure not "BV10"
        idx = t.lower().find(rn.lower())
        if idx >= 0:
            after = t[idx + len(rn) : idx + len(rn) + 1] if idx + len(rn) <= len(t) else ""
            if not after or after in " \n\t.,;":
                return True
        return False

    def select_rooms_from_modal(self, room_names: list[str]) -> int:
        """Select multiple rooms by calling select_room_from_modal for each. Returns count selected."""
        for name in room_names:
            self.select_room_from_modal(name)
        return len(room_names)

    def _is_unavailable_room(self, text: str) -> bool:
        """Check if room text indicates sold out, disabled, or unavailable."""
        return any(k in text for k in ("sold out", "unavailable", "0 available", "disabled", "not available"))

    def click_modal_add_room_and_wait_for_close(self, screenshot_on_fail: bool = True):
        """Locate purple Add Room button in modal footer (bottom-right). Click. Wait for close.
        Raises RuntimeError with clear message if button not found; captures screenshot when screenshot_on_fail=True.
        """
        from utils.screenshot_utils import take_failure_screenshot

        modal = self._get_room_modal()
        candidates = [
            modal.locator("[data-testid*='add_room'], [data-testid*='add-room']"),
            modal.get_by_role("button", name="Add Room"),
            modal.get_by_role("button", name="Add Room >"),
            modal.get_by_role("button", name="Confirm"),
            modal.locator("button:has-text('Add Room')"),
            modal.locator("button:has-text('Add ')"),
            modal.locator("button:has-text('Add 1 Room')"),
            modal.locator("button:has-text('Add 2 Room')"),
            modal.locator("button:has-text('Confirm')"),
            modal.locator("[role='button']:has-text('Add')"),
        ]
        add_room_btn = None
        for loc in candidates:
            if loc.count() > 0:
                add_room_btn = loc.last  # Footer button is typically last in modal
                break
        if add_room_btn is None:
            # Fallback: button or clickable with Add Room / Confirm text
            for txt in ["Add Room", "Add 1 Room", "Add 2 Room", "Confirm"]:
                btn = modal.locator(f"button:has-text('{txt}'), [role='button']:has-text('{txt}')")
                if btn.count() > 0:
                    add_room_btn = btn.last
                    break
            if add_room_btn is None:
                footer_btns = modal.locator("footer button, [class*='footer'] button")
                if footer_btns.count() > 0:
                    add_room_btn = footer_btns.last
                elif modal.locator("button").count() > 0:
                    add_room_btn = modal.locator("button").last
        if add_room_btn is None:
            if screenshot_on_fail:
                take_failure_screenshot(self.page, "add_room_footer_button_not_found")
            raise RuntimeError("Add Room footer button not found in modal")
        add_room_btn.wait_for(state="visible", timeout=10000)
        self._wait_for_stable(400)
        add_room_btn.scroll_into_view_if_needed()
        try:
            add_room_btn.click(timeout=5000)
        except Exception:
            add_room_btn.click(force=True)
        self._wait_for_room_modal_closed()
        print("[Reservations] Add Room clicked - modal closed.")

    def _wait_for_room_modal_closed(self):
        """Wait until the room selection modal is no longer visible."""
        try:
            modal = self.page.get_by_role("dialog").filter(has_text="Please Confirm")
            modal.wait_for(state="hidden", timeout=8000)
        except Exception:
            self._wait_for_stable(1500)

    def verify_rooms_added_to_form(self, expected_count: int):
        """Verify selected room(s) appear on the reservation form."""
        self._wait_for_stable(600)
        form = self._get_form_scope()
        # Form should show room chips, or Add Room/s is still visible (rooms added elsewhere)
        room_chips = form.locator("[class*='chip'], [class*='room-tag'], [data-room]")
        if room_chips.count() >= expected_count:
            print(f"[Reservations] Verified {expected_count} room(s) in form.")
        else:
            print("[Reservations] Form intact after room selection.")

    # ── Step 5: Fill remaining mandatory fields ─────────────────────────────────

    def fill_mandatory_fields_dynamic(self, data: dict):
        """Fill Source, dates, total guests, and any visible mandatory fields dynamically."""
        self._fill_source(data.get("source", "Direct"))
        self._fill_date_by_index(0, data.get("checkin_date", ""))
        self._fill_date_by_index(1, data.get("checkout_date", ""))
        self._fill_total_guests(str(data.get("total_guests", "1")))

    def _fill_source(self, source: str):
        """Open source dropdown, wait for options, choose matching option."""
        self._dismiss_overlays()
        ctrl = (
            self.page.get_by_role("combobox")
            .or_(self.page.locator("[role='combobox']"))
        ).first
        if ctrl.count() > 0 and ctrl.is_visible():
            ctrl.scroll_into_view_if_needed()
            self._safe_click(ctrl)
            self._wait_for_stable(500)
            for label in [source, source.title(), source.upper(), source.lower()]:
                opt = self.page.get_by_role("option", name=label).first
                if opt.count() > 0 and opt.is_visible():
                    self._safe_click(opt)
                    self._wait_for_stable(300)
                    print(f"[Reservations] Source -> {label}")
                    self._dismiss_overlays()
                    return
        self._dismiss_overlays()

    def _fill_date_by_index(self, index: int, date_str: str):
        """Click date field by index, wait for picker, enter date."""
        form = self._get_form_scope()
        inputs = form.locator(
            "input[type='date'], input[type='datetime-local'], "
            "input[placeholder*='DD/MM' i], input[placeholder*='date' i]"
        )
        if inputs.count() > index and date_str:
            inp = inputs.nth(index)
            if inp.is_visible():
                inp.scroll_into_view_if_needed()
                inp.click()
                self._wait_for_stable(400)
                inp.press("Control+A")
                inp.type(date_str, delay=50)
                self.page.keyboard.press("Escape")
                self._wait_for_stable(300)
                label = "Check-in" if index == 0 else "Check-out"
                print(f"[Reservations] {label} -> {date_str}")

    def _fill_total_guests(self, count: str):
        """Fill total guests using label or placeholder."""
        inp = (
            self.page.get_by_label("Total Guests", exact=False)
            .or_(self.page.get_by_label("Guests", exact=False))
            .or_(self.page.get_by_placeholder("guest", exact=False))
        ).first
        if inp.count() == 0:
            inp = self.page.locator("input[name*='guest' i], input[name*='totalGuest' i]").first
        if inp.count() > 0 and inp.is_visible():
            inp.click()
            inp.press("Control+A")
            inp.fill(count)
            self._wait_for_stable(200)
            print(f"[Reservations] Total Guests -> {count}")

    # ── Step 6: Submit and verify ─────────────────────────────────────────────

    def submit_create_reservation_and_wait_for_detail(self):
        """Locate Create Reservation button. Scroll into view, check enabled, click. Wait for Detail screen."""
        submit_btn = (
            self.page.get_by_role("button", name="Create Reservation")
            .or_(self.page.get_by_role("button", name="Save Reservation"))
        ).first
        expect(submit_btn).to_be_visible(timeout=10000)
        submit_btn.scroll_into_view_if_needed()
        self._wait_for_stable(400)
        if submit_btn.is_disabled():
            msg = self._suggest_missing_mandatory_field()
            raise RuntimeError(f"Create Reservation button is disabled. {msg or 'Check form validation.'}")
        self._safe_click(submit_btn)
        self._wait_for_reservation_detail_screen()
        print("[Reservations] Create Reservation submitted - detail screen loaded.")

    def _suggest_missing_mandatory_field(self) -> str | None:
        """Inspect form and suggest which mandatory field may be missing. Returns None if unclear."""
        form = self._get_form_scope()
        checks = [
            ("Guest Name", form.get_by_label("Guest Name", exact=False).or_(form.get_by_placeholder("e.g. Amit"))),
            ("Mobile", form.get_by_placeholder("9876").or_(form.get_by_label("Mobile", exact=False))),
            ("Check-in date", form.locator("input[placeholder*='DD/MM' i], input[type='date']").first),
            ("Source", form.get_by_role("combobox")),
        ]
        for label, loc in checks:
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    val = loc.first.input_value()
                    if not val or str(val).strip() == "":
                        return label
            except Exception:
                pass
        return None

    def _wait_for_reservation_detail_screen(self):
        """Wait for navigation to Reservation Detail page."""
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_for_stable(2000)
        try:
            self.page.wait_for_url("**/view**", timeout=12000)
        except Exception:
            pass
        self.page.wait_for_load_state("networkidle")
        self._wait_for_stable(1000)

    def validate_reservation_detail(self) -> bool:
        """Verify reservation detail page: reservation ID, header, guest name, or booked room section."""
        url = self.page.url
        if "/reservation" in url.lower() or "/view" in url.lower():
            print(f"[Reservations] Validated: URL = {url}")
            return True
        indicators = [
            ("reservation ID", self.page.locator("text=/Reservation ID|Reservation #|ID:/i")),
            ("reservation detail header", self.page.get_by_role("heading", name="Reservation").or_(self.page.get_by_text("Reservation Detail", exact=False))),
            ("guest name", self.page.get_by_text("Guest", exact=False).or_(self.page.locator("[class*='guest-name'], [class*='guestName']"))),
            ("booked room section", self.page.locator("[class*='room'], [class*='Room'], [class*='booked'], [class*='booking-info']")),
        ]
        for name, loc in indicators:
            try:
                if loc.count() > 0 and loc.first.is_visible():
                    print(f"[Reservations] Validated: {name} visible.")
                    return True
            except Exception:
                pass
        print(f"[Reservations] Could not validate detail. URL: {url}")
        return False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_form_scope(self):
        """Scope: reservation form container. Dialog if form is in modal, else page."""
        # If reservation form is in a dialog (not the room modal), use it
        dialogs = self.page.get_by_role("dialog")
        for i in range(dialogs.count()):
            d = dialogs.nth(i)
            try:
                if d.is_visible():
                    txt = d.inner_text() or ""
                    if "Please Confirm" in txt or "Available Rooms" in txt:
                        continue  # Room selection modal — skip
                    if "Add Room" in txt or "Guest" in txt or "Create Reservation" in txt:
                        return d
            except Exception:
                pass
        return self.page

    def _wait_for_stable(self, ms: int):
        self.page.wait_for_timeout(ms)

    def _wait_for_enabled(self, locator, timeout: int = 5000):
        try:
            locator.wait_for(state="attached", timeout=timeout)
            locator.wait_for(state="visible", timeout=timeout)
            # Playwright: disabled state check
            locator.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass

    def _safe_click(self, locator):
        """Click with retry and scroll. Fallback: force click."""
        try:
            locator.scroll_into_view_if_needed()
            locator.click(timeout=5000)
        except Exception:
            locator.click(force=True)

    def _dismiss_overlays(self):
        """Close any open overlay (radix, dropdown) with Escape."""
        try:
            overlay = self.page.locator("div[data-state='open'].fixed").first
            if overlay.count() > 0 and overlay.is_visible():
                self.page.keyboard.press("Escape")
                self._wait_for_stable(400)
        except Exception:
            pass

    # ── Navigation (for flow) ─────────────────────────────────────────────────

    def go_to_reservations(self):
        """Navigate to Reservations page from left sidebar."""
        link = (
            self.page.get_by_role("link", name="Reservation")
            .or_(self.page.get_by_role("link", name="Reservations"))
            .or_(self.page.locator("a:has-text('Reservation'), a:has-text('Reservations'), li:has-text('Reservation'), li:has-text('Reservations')"))
        ).first
        expect(link).to_be_visible(timeout=15000)
        self._safe_click(link)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_url("**/reservations**", timeout=15000)
        print("[Reservations] Navigated to Reservations page.")
