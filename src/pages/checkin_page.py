from pathlib import Path
from playwright.sync_api import Page, expect


class CheckinPage:
    def __init__(self, page: Page):
        self.page = page

        self.checkin_heading = page.locator("text=Check-in").first
        self.id_proof_step = page.locator("text=ID Proof").first
        self.basic_details_step = page.locator("text=Basic Details").first

        self.guest_card = page.locator("text=Guest 01").first
        self.indian_radio = page.locator("text=Indian").first
        self.foreign_radio = page.locator("text=Foreign").first

        self.add_id_btn = page.locator(
            "button:has-text('Add ID'), button:has-text('Upload ID')"
        ).first

        # Front / Back Aadhar: file inputs found by label/section text or by order (first = front, second = back)
        self._file_inputs = page.locator("input[type=file]")
        self._front_upload_section = page.locator("text=/front.*(id|aadhar)|(id|aadhar).*front|upload.*front/i").first
        self._back_upload_section = page.locator("text=/back.*(id|aadhar)|(id|aadhar).*back|upload.*back/i").first

        self.continue_btn = page.get_by_role("button", name="Continue").first
        self.next_btn = page.get_by_role("button", name="Next").first
        self.save_btn = page.get_by_role("button", name="Save").first

        # Basic Details screen — Contact No field (placeholder: "e.g. 623012306")
        self.contact_no_input = page.locator(
            "input[placeholder*='623012306'], "
            "input[placeholder*='e.g.'], "
            "[name='mobile'], "
            "[name='phone'], "
            "[name='contactNo'], "
            "[name='contact'], "
            "input[placeholder*='Mobile' i], "
            "input[placeholder*='Contact' i]"
        ).first

        # Keep legacy field locators in case other steps use them
        self.first_name_input = page.locator(
            "[name='firstName'], input[placeholder*='First Name' i]"
        ).first
        self.last_name_input = page.locator(
            "[name='lastName'], input[placeholder*='Last Name' i]"
        ).first
        self.mobile_input = self.contact_no_input
        self.email_input = page.locator(
            "[name='email'], input[placeholder*='Email' i]"
        ).first

        self.advance_input = page.locator(
            "input[placeholder*='advance' i], input[placeholder*='Advance' i]"
        ).first

        self.complete_checkin_btn = page.locator(
            "button:has-text('CHECK IN'), "
            "button:has-text('Check In'), "
            "button:has-text('Complete Check-in'), "
            "button:has-text('Complete Checkin')"
        ).first

        # "Looks Good?" confirmation dialog that appears after each ID upload
        self.confirm_btn = page.get_by_role("button", name="Confirm").first

        # Use .or_() chaining to avoid regex-flag parsing bugs with comma-separated selectors
        self.success_message = (
            page.locator("text=/checked.?in.?successfully/i")
            .or_(page.locator("text=/check.?in.*success/i"))
            .or_(page.locator("text=/guest.*checked/i"))
            .or_(page.locator("text=Successfully"))
        )

    def wait_for_checkin_flow_to_open(self):
        expect(self.checkin_heading).to_be_visible(timeout=15000)
        expect(self.id_proof_step).to_be_visible(timeout=10000)
        expect(self.guest_card).to_be_visible(timeout=10000)

    def select_indian_if_available(self):
        try:
            if self.indian_radio.count() > 0 and self.indian_radio.is_visible():
                self.indian_radio.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

    def _resolve_path(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.is_absolute():
            path = path.resolve()
        abs_path = str(path)
        if not Path(abs_path).exists():
            raise FileNotFoundError(f"ID document file not found: {abs_path}")
        return abs_path

    def _get_front_file_input(self):
        """Find file input for Front ID / Front Aadhar upload (search for 'front id upload' / 'front aadhar')."""
        if self._front_upload_section.count() > 0 and self._front_upload_section.is_visible():
            # Input inside same section or in parent
            for loc in [
                self._front_upload_section.locator("input[type=file]").first,
                self._front_upload_section.locator("..").locator("input[type=file]").first,
            ]:
                if loc.count() > 0:
                    return loc
        if self._file_inputs.count() >= 1:
            return self._file_inputs.first
        return None

    def _get_back_file_input(self):
        """Find file input for Back ID / Back Aadhar upload (search for 'back id upload' / 'back aadhar')."""
        if self._back_upload_section.count() > 0 and self._back_upload_section.is_visible():
            for loc in [
                self._back_upload_section.locator("input[type=file]").first,
                self._back_upload_section.locator("..").locator("input[type=file]").first,
            ]:
                if loc.count() > 0:
                    return loc
        if self._file_inputs.count() >= 2:
            return self._file_inputs.nth(1)
        return None

    def _click_add_id_and_wait_for_upload_ui(self, timeout_ms: int = 8000):
        """Click 'Add ID' and wait for the upload UI (file input or front/back section) to appear."""
        if self.add_id_btn.count() > 0 and self.add_id_btn.is_visible():
            self.add_id_btn.click()
            self.page.wait_for_timeout(500)
        # Wait for at least one file input or upload area to appear (no native file chooser)
        try:
            self.page.locator("input[type=file]").first.wait_for(state="attached", timeout=timeout_ms)
            self.page.wait_for_timeout(800)
        except Exception:
            pass

    def click_add_id_and_open_upload_ui(self, timeout_ms: int = 8000):
        """Always click 'Add ID' (even before file availability is known) and wait for upload section."""
        expect(self.add_id_btn).to_be_visible(timeout=10000)
        self.add_id_btn.click()
        self.page.wait_for_timeout(500)
        # Wait for upload inputs to appear after Add ID is clicked
        try:
            self.page.locator("input[type=file]").first.wait_for(state="attached", timeout=timeout_ms)
            self.page.wait_for_timeout(800)
        except Exception:
            self.page.wait_for_timeout(1000)

    def _wait_for_nth_file_input(self, n: int, timeout_ms: int = 8000):
        """Wait until at least n+1 file inputs are attached (app may reveal back input after front upload)."""
        try:
            self.page.wait_for_function(
                f"document.querySelectorAll('input[type=file]').length > {n}",
                timeout=timeout_ms,
            )
            self.page.wait_for_timeout(500)
        except Exception:
            pass

    def _click_confirm_with_retry(self, label: str = "", timeout_ms: int = 10000):
        """Wait for Confirm to appear, scroll to it, click it, then verify dialog dismissed.
        Retries once if first click didn't dismiss. Falls back to Escape."""
        # Try multiple selectors in case role/name doesn't match exactly
        confirm_locators = [
            self.page.get_by_role("button", name="Confirm").first,
            self.page.locator("button:has-text('Confirm')").first,
            self.page.locator("text=Confirm").first,
        ]

        clicked = False
        for loc in confirm_locators:
            try:
                loc.wait_for(state="visible", timeout=timeout_ms)
                loc.scroll_into_view_if_needed()
                self.page.wait_for_timeout(300)
                loc.click()
                self.page.wait_for_timeout(1000)
                clicked = True
                print(f"[ID upload] {label} Confirm clicked.")
                break
            except Exception:
                continue

        if not clicked:
            print(f"[ID upload] {label} Confirm not found within {timeout_ms}ms — pressing Escape.")
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(800)
            except Exception:
                pass
            return

        # Verify dialog was dismissed; if "Looks Good?" still visible, retry once
        try:
            looks_good = self.page.locator("text=Looks Good").first
            if looks_good.count() > 0 and looks_good.is_visible():
                print(f"[ID upload] {label} dialog still open after Confirm — retrying click.")
                for loc in confirm_locators:
                    try:
                        if loc.count() > 0 and loc.is_visible():
                            loc.scroll_into_view_if_needed()
                            loc.click()
                            self.page.wait_for_timeout(1000)
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    def _close_add_id_dialog_if_open(self):
        """Close the Add ID dialog after all uploads are confirmed.
        Tries (in order): X close button, overlay click, Escape key."""
        try:
            add_id_heading = self.page.locator("text=Add ID").first
            if not (add_id_heading.count() > 0 and add_id_heading.is_visible()):
                return  # dialog already closed
        except Exception:
            return

        print("[ID upload] Add ID dialog still open after Confirm — trying to close it.")

        # 1. Try clicking the X / close button inside the dialog
        close_selectors = [
            "button[aria-label='Close']",
            "button[aria-label='close']",
            "[role='dialog'] button:has(svg)",
            "button.close",
            "button:has-text('×')",
            "button:has-text('✕')",
        ]
        for sel in close_selectors:
            try:
                btn = self.page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click()
                    self.page.wait_for_timeout(800)
                    print(f"[ID upload] Closed dialog using: {sel}")
                    return
            except Exception:
                continue

        # 2. Try clicking outside the dialog (the backdrop)
        try:
            self.page.mouse.click(10, 10)
            self.page.wait_for_timeout(800)
            add_id_heading = self.page.locator("text=Add ID").first
            if not (add_id_heading.count() > 0 and add_id_heading.is_visible()):
                print("[ID upload] Closed dialog by clicking backdrop.")
                return
        except Exception:
            pass

        # 3. Press Escape
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(1000)
            print("[ID upload] Closed dialog with Escape key.")
        except Exception:
            pass

    def set_front_and_back_id_files(self, front_path: str, back_path: str):
        """Upload front ID and (optionally) back ID.

        Flow:
          1. Upload front → wait for preview → click Confirm (with retry + fallback)
          2. Check if a back file input appears (not all apps need back)
          3. If back input appears → upload back → click Confirm
          4. Force-close dialog with Escape if still open
        """
        front_abs = self._resolve_path(front_path)
        back_abs = self._resolve_path(back_path)

        # ── Upload Front ──
        front_inp = self._get_front_file_input()
        if not front_inp:
            raise Exception("Front ID upload input not found after clicking Add ID.")
        print("[ID upload] Uploading front ID...")
        front_inp.set_input_files(front_abs)
        self.page.wait_for_timeout(2500)  # let preview render

        # ── Confirm front ──
        self._click_confirm_with_retry(label="Front", timeout_ms=10000)

        # After front Confirm, the front input disappears and a NEW single back
        # input appears (count resets to 1, not > 1). Wait for count >= 1.
        print("[ID upload] Checking if back ID input appears after front confirm...")
        try:
            self.page.wait_for_function(
                "document.querySelectorAll('input[type=file]').length >= 1",
                timeout=5000,
            )
            self.page.wait_for_timeout(500)
            back_appeared = True
        except Exception:
            back_appeared = False

        if back_appeared:
            back_inp = self.page.locator("input[type=file]").first
            if back_inp.count() > 0:
                print("[ID upload] Back ID input found — uploading back ID...")
                back_inp.set_input_files(back_abs)
                self.page.wait_for_timeout(2500)
                self._click_confirm_with_retry(label="Back", timeout_ms=10000)
            else:
                print("[ID upload] File input gone — back upload skipped.")
        else:
            print("[ID upload] No back ID input appeared — front-only upload assumed complete.")

        # Close dialog if still open
        self._close_add_id_dialog_if_open()

    def set_single_id_file(self, file_path: str):
        """Upload a single ID file into the already-open upload UI (call after click_add_id_and_open_upload_ui)."""
        abs_path = self._resolve_path(file_path)
        file_input = self.page.locator("input[type=file]").first
        if file_input.count() > 0:
            file_input.set_input_files(abs_path)
            self.page.wait_for_timeout(1500)
        else:
            raise Exception("No file input found after clicking Add ID.")

    def upload_guest_id_front_back(self, front_path: str, back_path: str):
        """Upload front Aadhar and back Aadhar using the correct PNGs from data. Clicks Upload ID if needed."""
        front_abs = self._resolve_path(front_path)
        back_abs = self._resolve_path(back_path)

        self._click_add_id_and_wait_for_upload_ui()

        # Upload Front ID
        front_inp = self._get_front_file_input()
        if front_inp:
            front_inp.set_input_files(front_abs)
            self.page.wait_for_timeout(1200)
        else:
            raise FileNotFoundError("Front ID upload input not found on page. Look for 'Front ID upload' / 'Front Aadhar'.")

        # Upload Back ID
        back_inp = self._get_back_file_input()
        if back_inp:
            back_inp.set_input_files(back_abs)
            self.page.wait_for_timeout(1200)
        else:
            raise FileNotFoundError("Back ID upload input not found on page. Look for 'Back ID upload' / 'Back Aadhar'.")
        self.page.wait_for_timeout(500)

    def upload_guest_id(self, file_path: str):
        path = Path(file_path)
        if not path.is_absolute():
            path = path.resolve()
        absolute_file_path = str(path)
        if not Path(absolute_file_path).exists():
            raise FileNotFoundError(f"ID document file not found: {absolute_file_path}")

        # Click "Add ID" first so the app reveals the file input (no native file chooser on this UI)
        self._click_add_id_and_wait_for_upload_ui()

        # Set file on the first available input[type=file]
        file_input = self.page.locator("input[type=file]").first
        if file_input.count() > 0:
            file_input.set_input_files(absolute_file_path)
            self.page.wait_for_timeout(1500)
            return

        # Last resort: wait for native file chooser (only if app actually opens one)
        try:
            with self.page.expect_file_chooser(timeout=5000) as fc_info:
                if self.add_id_btn.count() > 0 and self.add_id_btn.is_visible():
                    self.add_id_btn.click()
            file_chooser = fc_info.value
            file_chooser.set_files(absolute_file_path)
            self.page.wait_for_timeout(2000)
        except Exception:
            raise FileNotFoundError(
                "No file input found after clicking Add ID. The app may use a custom upload; ensure input[type=file] exists in the ID section."
            )

    def _wait_for_primary_btn_enabled(self, timeout_ms: int = 12000):
        """Wait for Continue, Next, or Save to be visible AND enabled.
        Polls for up to timeout_ms in case the button appears after dialog closes."""
        import time
        deadline = time.time() + timeout_ms / 1000
        poll = 500
        while time.time() < deadline:
            for btn in (self.continue_btn, self.next_btn, self.save_btn):
                try:
                    if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                        return btn
                except Exception:
                    pass
            try:
                self.page.wait_for_timeout(poll)
            except Exception:
                # Page/browser closed during wait — stop polling
                return None
        return None

    def click_primary_next(self):
        btn = self._wait_for_primary_btn_enabled()
        if btn:
            btn.click()
            self.page.wait_for_timeout(1000)
            return

        # Give it one last look after a short pause (dialog may have just closed)
        self.page.wait_for_timeout(1500)
        for btn in (self.continue_btn, self.next_btn, self.save_btn):
            try:
                if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                    btn.click()
                    self.page.wait_for_timeout(1000)
                    return
            except Exception:
                pass

        # Report what was found to help diagnose
        disabled_names = []
        for name, btn in [("Continue", self.continue_btn), ("Next", self.next_btn), ("Save", self.save_btn)]:
            try:
                if btn.count() > 0 and btn.is_visible():
                    disabled_names.append(name)
            except Exception:
                pass
        if disabled_names:
            raise Exception(
                f"{', '.join(disabled_names)} button(s) visible but still disabled. "
                "ID upload may not have completed — check that front Aadhar PNG exists and Confirm was clicked."
            )
        raise Exception(
            "Continue / Next / Save button not found. "
            "The Add ID dialog may still be open. Check that Confirm was clicked after upload."
        )

    def wait_for_basic_details_screen(self):
        expect(self.basic_details_step).to_be_visible(timeout=15000)

    def fill_basic_details(self, guest_data: dict):
        """Fill the Basic Details screen.

        The screen shows:
          - Contact No  (placeholder: e.g. 623012306)  ← filled from guest_data["mobile"]
          - Check-out date                             ← pre-filled, not touched
          - Rooms / Room Rate                          ← pre-filled, not touched
          - Advance payment                            ← optional, not filled unless provided
        """
        mobile = guest_data.get("mobile", "")
        if mobile:
            try:
                self.contact_no_input.wait_for(state="visible", timeout=8000)
                self.contact_no_input.clear()
                self.contact_no_input.fill(mobile)
                print(f"[Basic Details] Contact No filled: {mobile}")
            except Exception as e:
                print(f"[Basic Details] Could not fill Contact No: {e}")

        # Fill first name / last name / email if they appear on this screen (optional)
        for field, key in [
            (self.first_name_input, "first_name"),
            (self.last_name_input, "last_name"),
            (self.email_input, "email"),
        ]:
            try:
                if field.count() > 0 and field.is_visible():
                    field.fill(guest_data.get(key, ""))
            except Exception:
                pass

    def complete_checkin(self):
        expect(self.complete_checkin_btn).to_be_visible(timeout=15000)
        self.complete_checkin_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(300)
        print(f"[Check-in] Clicking CHECK IN button...")
        self.complete_checkin_btn.click()

    def verify_checkin_success(self):
        try:
            expect(self.success_message).to_be_visible(timeout=15000)
            print("[Check-in] Success message visible — check-in completed.")
        except Exception:
            # The app may redirect to another page instead of showing a toast.
            # Consider check-in done if the URL no longer contains 'new-check-in'.
            current_url = self.page.url
            if "new-check-in" not in current_url:
                print(f"[Check-in] No success toast found, but page navigated away → {current_url} — treating as success.")
            else:
                raise