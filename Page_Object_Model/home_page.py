from time import sleepfrom selenium.webdriver.common.by import Byfrom Utility.global_driver_utils import AbstractComponentfrom allure import stepclass home_page_model(AbstractComponent):    def __init__(self, driver):        super().__init__(driver)    __SIGN_UP = (By.CSS_SELECTOR, 'a[href*="register"]')    @step("click on the Sign up button on Dashboard")    def click_sign_up_button(self):        self.click_button(*home_page_model.__SIGN_UP)        sleep(4)        print("Saket")