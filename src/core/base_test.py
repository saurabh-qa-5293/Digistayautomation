import pytest
from playwright.sync_api import sync_playwright
from config.setting import HEADLESS, DEFAULT_TIMEOUT

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture()
def page(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=HEADLESS)
    context = browser.new_context(no_viewport=True)
    context.set_default_timeout(DEFAULT_TIMEOUT)

    page = context.new_page()
    yield page

    context.close()
    browser.close()