from appium import webdriver

caps = {}
caps['platformName'] = 'Android'
caps['deviceName'] = 'Google Pixel'
caps['automationName'] = 'UiAutomator2'
caps['appPackage'] = 'com.android.launcher3'
caps['appActivity'] = 'com.android.launcher3.Launcher'

driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)

camera_path = '/mnt/sdcard/DCIM/Camera'
rm_camera_command = {
    'command': 'rm',
    'args': ['-rf', '/mnt/sdcard/DCIM/Camera/*.*']
}
ls_camera_command = {
    'command': 'ls',
    'args': ['/mnt/sdcard/DCIM/Camera']
}
ls_output_before_rm = driver.execute_script('mobile:shell', ls_camera_command)
driver.execute_script('mobile:shell', rm_camera_command)
ls_output_after_rm = driver.execute_script('mobile:shell', ls_camera_command)
print("执行删除文件前的ls命令结果", ls_output_before_rm)
print("执行删除文件后的ls命令结果", ls_output_after_rm)



