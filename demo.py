import time

from appium import webdriver

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.videogo'
caps['appActivity'] = 'com.videogo.main.MainTabActivity'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

time.sleep(10)




