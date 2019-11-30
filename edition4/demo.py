from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['browserName'] = 'Chrome'
# caps['appPackage'] = 'com.android.browser'
# caps['appActivity'] = 'com.uc.browser.InnerUCMobile'



EMAIL = (By.ID, "contactEmail")
MESSAGE = (By.ID, "contactText")
SEND = (By.CSS_SELECTOR, "input[type=submit]")
ERROR = (By.CSS_SELECTOR, ".contactResponse")

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

wait = WebDriverWait(driver, 10);

driver.get("http://appiumpro.com/contact")

wait.until(expected_conditions.visibility_of(EMAIL)).send_keys("77936430@qq.com")
