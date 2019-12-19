from appium import webdriver

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.android.launcher3'
caps['appActivity'] = 'com.android.launcher3.Launcher'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

driver