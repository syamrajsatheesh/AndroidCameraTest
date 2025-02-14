# -- coding: utf-8 --
import os
from time import sleep
import time
import unittest
import sys
import requests
from appium import webdriver


class SimpleAndroidTests(unittest.TestCase):

    def setUp(self):
        self.udid = sys.argv[1]
        self.url = sys.argv[2]
        self.package= "com.google.android.gm"
        self.activity = "com.google.android.gm.ui.MailActivityGmail"
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['deviceName'] = self.udid
        desired_caps['udid'] = self.udid
        desired_caps['appPackage'] = self.package
        desired_caps['appActivity'] = self.activity
        desired_caps['noReset'] = True
      

        self.driver = webdriver.Remote(self.url, desired_caps)


        self.status = "Fail_Launch"
        
    def tearDown(self):
        
        self.driver.quit()
       
    
    def test_template_matcher(self):
        self.driver.implicitly_wait(50)
        self.load_screensize('Vertical')
        self.launch()
        sleep(5)
        self.take_screenshots()

    def launch(self):
        compose_btn=self.driver.find_element_by_id("com.google.android.gm:id/compose_button")
        self.driver.implicitly_wait(5)
        for i in range(0,15):
            try:
                # mail=self.driver.find_element_by_android_uiautomator('text("2 Template Matching")')
                mail=self.driver.find_element_by_android_uiautomator('text("4 Template Matching")')
                mail.click()
                break
            except:
                self.driver.swipe( self.thumb_s_x, self.thumb_s_y,self.thumb_e_x, self.thumb_e_y, 200)
        self.driver.implicitly_wait(50)

        image = self.driver.find_element_by_class_name("android.widget.Image") 
        print("mail opened")

    def take_screenshots(self):
        self.driver.implicitly_wait(5)
        for i in range (0,15):
            directory = '%s/' % os.getcwd()
            file_name = f'{self.udid}_{i}_google.png'
            try:
                reply_btn = self.driver.find_element_by_id('com.google.android.gm:id/reply_button')
                self.driver.save_screenshot(directory + file_name)
                print(directory + file_name)
                break
            except:
                self.driver.save_screenshot(directory + file_name)
                print(directory + file_name)
                self.driver.swipe( self.thumb_s_x, self.thumb_s_y,self.thumb_e_x, self.thumb_e_y, 200)

    def load_screensize(self, direction = None):
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        # Horizontal scroll cordinates
        self.thumb_s_x = width * 0.75
        self.thumb_s_y = height * 0.25
        self.thumb_e_x = width * 0.25
        self.thumb_e_y = height *0.25
        self.width = width
        self.height = height

        if direction in ("Vertical", "vertical","V","v"):
            self.thumb_s_x = width /2
            self.thumb_s_y = height * 0.5
            self.thumb_e_x = width / 2
            self.thumb_e_y = height * 0.3

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)


