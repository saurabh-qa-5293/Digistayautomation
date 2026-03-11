class ForgotPasswordPage:
    def __init__(self, page):
        self.page = page

    def verify_loaded(self):
        self.page.get_by_test_id("auth__forgot_password__page").wait_for()

    def fill_email(self, email):
        self.page.get_by_test_id("auth__forgot_password__email__input").fill(email)

    def click_submit(self):
        self.page.get_by_test_id("auth__forgot_password__submit__btn").click()

    def click_back_to_login(self):
        self.page.get_by_test_id("auth__forgot_password__back_to_login__link").click()

    def verify_success_message(self):
        self.page.get_by_test_id("auth__forgot_password__success__message").wait_for()