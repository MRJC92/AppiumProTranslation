import base64
import os
import time

from appium import webdriver


def change_img_as_base64(img_name):
    with open(img_name, 'rb') as f:
        return base64.b64encode(f.read())

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.android.gallery3d'
caps['appActivity'] = 'com.android.gallery3d.app.GalleryActivity'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

# 这里我死等待5s，是为了让效果更加明显一点，因为刚开始的时候它会弹出当前没有照片的toast
time.sleep(5)
# 由于我选择的模拟器打开相册应用不会有其他界面，直接进入了显示照片的界面，所以我这里不需要操作
img = 'Android.jpg'
img_path = os.path.abspath(img)
device_photo_path = '/sdcard/Pictures'
driver.push_file(device_photo_path+'/'+img, source_path=img)





