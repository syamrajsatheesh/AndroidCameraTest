
from time import sleep
import os
import socket
import sh
import time
import unittest
import logging
import datetime
import sys
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
import  requests
class SimpleAndroidTests(unittest.TestCase):


    
    def setUp(self):
		

        self.test_name  ="BBC test"
        self.package= "com.google.android.youtube"
        self.udid = sys.argv[1]
        self.device_id = self.udid
        self.os='Android'
        desired_caps = {}
        desired_caps['platformName'] = self.os
        desired_caps['udid'] = self.udid
        desired_caps['deviceName'] = self.udid
        desired_caps['appPackage'] = "com.google.android.youtube"
        desired_caps['appActivity'] = "com.google.android.youtube.HomeActivity"
        desired_caps['noReset'] = 'True'
        desired_caps['headspin:capture.video'] = True
        desired_caps['headspin:capture.network'] = False

        appium_input= sys.argv[2]

        self.url = appium_input
        self.access_token = self.url.split('/')[4]
        if appium_input.isdigit():
                self.url= ('http://127.0.0.1:' + appium_input + '/wd/hub')
        else:
                self.url= appium_input
        self.driver = webdriver.Remote(self.url, desired_caps)
        self.status = "Fail"

    def tearDown(self):

        if "Fail" in self.status:
            session_status = "Failed"
        else:
            session_status = "Passed"

        self.session_id  =self.driver.session_id
        api_endpoint= "https://api-dev.headspin.io/v0/perftests/upload"
        session_data = {"session_id": self.session_id, "test_name": self.test_name,"status": session_status,"data": [{"key": "status", "value": self.status}]}
        r = requests.post(api_endpoint, headers={'Authorization': 'Bearer {}'.format(self.access_token)}, json=session_data)
        result = r.json()
        print(r.text)
        print("Performance session added")


        data_payload = {}
        description_string = "status : "+ str(self.status) + "\n" 
        data_payload['name'] = self.test_name
        data_payload['description'] = description_string
        request_url = 'https://api-dev.headspin.io/v0/sessions/' + self.session_id + '/description'
        response = requests.post(request_url, headers={'Authorization': 'Bearer {}'.format(self.access_token)}, json=data_payload)
        print(response.text)
        print(response)
        print("Description added")

        self.driver.quit()

    def test_login(self):


        self.session_id = self.driver.session_id
        api_endpoint = "https://api-dev.headspin.io/v0/sessions/tags/{}".format(self.session_id)
        session_data=[{"session type":"video"}]
        r = requests.post(api_endpoint, headers={'Authorization': 'Bearer {}'.format(self.access_token)}, json=session_data)
        print(r.text)
        print("Tag added")



        self.driver.implicitly_wait(30)
        search = self.driver.find_element_by_accessibility_id("Search")
        search.click()

        search_bar  = self.driver.find_element_by_id("com.google.android.youtube:id/search_edit_text")
        search_bar.click()
        search_bar.send_keys("BBC earth")
        self.driver.press_keycode(66)

        #choose bbc earth chanel from the result
        try:
            ch = self.driver.find_element_by_android_uiautomator('new UiSelector().text("BBC Earth")')
        except :
            ch = self.driver.find_element_by_id("com.google.android.youtube:id/channel_name")

        ch.click()

        sleep(2)
        
        try:
            video_tab = self.driver.find_element_by_accessibility_id("Videos")
            video_tab.click()
        except :
            print("Switch to video failed")

        videos = self.driver.find_elements_by_android_uiautomator('new UiSelector().descriptionContains("play video")')
        videos[0].click()

        sleep(5)
    
        #ad mngmnt
        t_end = time.time() + 20
        self.driver.implicitly_wait(2)
        while time.time() < t_end :
            try:    
                skip_ad = self.driver.find_element_by_id("com.google.android.youtube:id/skip_ad_button_icon").click()
                print("ad skipped...")
                break
            except:
                pass

        #full screen
        t_end = time.time() + 20
        self.driver.implicitly_wait(1)
        while time.time() < t_end :
            try:    
                self.driver.press_keycode(62)
                self.driver.find_element_by_id("com.google.android.youtube:id/fullscreen_button").click()
                print("Full screen...")
                break
            except:
                try:
                    self.driver.find_element_by_id("com.google.android.youtube:id/fullscreen_button").click()
                except :
                    print("full screen fail")
        


        os.mkdir(self.driver.session_id)
        os.chdir(self.driver.session_id)


        #screen capture thing
        t_end = time.time() + 180
        self.driver.implicitly_wait(1)
        
        while time.time() < t_end :
            try:    
                name = str(time.time())
                name = name +".png"
                self.driver.save_screenshot(name)
                print("taking screenshot...")
                sleep(5)
                self.status = "Pass"
            except Exception as e:
                print(e)
                sleep(5)

        print("Pass")
        self.status = "Pass"


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)





                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
