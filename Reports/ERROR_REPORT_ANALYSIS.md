# Error Report Analysis (Auto-generated)

## Latest failure summary

| Field | Value |
|-------|--------|
| **Test** | `tests/test_checkin_from_room_view.py::TestCheckinFromRoomView::test_checkin_from_room_view` |
| **Error type** | `playwright._impl._errors.TimeoutError` |
| **Message** | `Locator.click: Timeout 30000ms exceeded` |
| **Location** | `src\flows\checkin_flow.py:36` → `src\pages\checkin_page.py:90` (`click_primary_next` → `next_btn.click()`) |

---

## Root cause

The **Next** button is **found but disabled**:

- **Call log:** `get_by_role("button", name="Next").first` resolved to a `<button disabled ...>`.
- Playwright waits for the element to be **visible, enabled and stable** before clicking.
- The button never becomes enabled → 30s timeout.

**Why it’s disabled:**  
The app keeps **Next** disabled on the ID Proof step until an ID document is uploaded. The test currently **skips** the ID upload when the file is missing (`data/Adhar_ FRont.png`), so the button never enables.

---

## Fix applied

1. **Wait for the primary button to be enabled** before clicking (in `checkin_page.py`). If it stays disabled (e.g. ID not uploaded), fail with a short timeout and a clear message instead of a long generic timeout.
2. **To make the test pass:** Add the ID image at `data/Adhar_ FRont.png` (or update `document_file` in `data/guest_data.json`) so the upload runs and **Next** becomes enabled.

---

## Past errors (for reference)

| Error | Cause | Resolution |
|-------|--------|------------|
| `AttributeError: 'CheckinFlow' object has no attribute 'complete_checkin_flow'` | Missing method | Added `complete_checkin_flow()` in `CheckinFlow`. |
| `TimeoutError: filechooser` | Add ID doesn’t open native dialog / no `input[type=file]` | Try `input[type=file].set_input_files()` first; fallback to file chooser; skip upload if file missing. |
| `Continue / Next / Save button not found` | Wrong step or UI | Resolved by correct flow; if ID skipped, Next can stay disabled (see above). |
| `FileNotFoundError: ...\src\data\Adhar_ FRont.png` | Wrong project root | Use `parents[2]` so path is `project_root/data/...`. |
| **Next button timeout (current)** | Next disabled until ID uploaded | Wait for button enabled; add ID file to pass. |
