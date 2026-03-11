import sys
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(
        permissions=["camera", "microphone"]
    )
    page = context.new_page()
    yield page
    context.close()