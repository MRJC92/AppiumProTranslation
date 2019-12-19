from appium import webdriver
import time 

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.android.gallery3d'
caps['appActivity'] = 'com.android.gallery3d.app.GalleryActivity'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

result = driver.get_performance_data('com.android.gallery3d', 'memoryinfo', 5)
print(result)

