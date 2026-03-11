from pathlib import Path
from datetime import datetime


def take_failure_screenshot(page, test_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = Path("reports/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    file_path = screenshots_dir / f"{test_name}_{timestamp}.png"
    page.screenshot(path=str(file_path), full_page=True)
    return str(file_path)