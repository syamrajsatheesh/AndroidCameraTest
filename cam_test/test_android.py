from time import sleep
import os
# import socket
# import sh
import time
import unittest
import psycopg2
import six.moves.configparser
# import logging
# import datetime
import sys
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
import requests


class SimpleAndroidTests(unittest.TestCase):
    #     "automationName": "UiAutomator2",

    def setUp(self):

        self.test_name = "camera test"
        self.package = "com.apple.camera"
        self.udid = "RF8M33MPALX"
        self.device_id = self.udid
        self.os = 'Android'
        desired_caps = {}
        desired_caps['platformName'] = self.os
        desired_caps['udid'] = self.udid
        desired_caps['deviceName'] = "SM-G973U1"
        desired_caps['bundleId'] = "com.apple.camera"
        desire_caps['appPackage'] = "com.sec.android.app.camera"
        desired_caps['appActivity'] = "com.sec.android.app.camera.Camera"
        desired_caps['noReset'] = 'True'
        desired_caps['headspin:capture.video'] = True
        desired_caps['headspin:capture.network'] = False

        #"https://dev-us-pao-1.headspin.io:7031/v0/3775ed42bfa04fa8a48898592c251b68/wd/hub"
        appium_input= sys.argv[2]

        self.url = appium_input
        self.access_token = self.url.split('/')[4]
        if appium_input.isdigit():
                self.url= ('http://127.0.0.1:' + appium_input + '/wd/hub')
        else:
                self.url= appium_input
        self.driver = webdriver.Remote(self.url, desired_caps)
        self.start=int(round(time.time() * 1000))
        self.status = "Fail"

    def tearDown(self):

        if "Fail" in self.status:
            session_status = "Failed"
        else:
            session_status = "Passed"

        self.session_id = self.driver.session_id
        api_endpoint = "https://api-dev.headspin.io/v0/perftests/upload"
        session_data = {"session_id": self.session_id, "test_name": self.test_name, "status": session_status,
                        "data": [{"key": "status", "value": self.status}]}
        r = requests.post(api_endpoint, headers={'Authorization': 'Bearer {}'.format(self.access_token)},
                          json=session_data)
        result = r.json()
        print(r.text)
        print("Performance session added")

        self.driver.quit()
        # sleep(500)

        # syncing session to DB
        print("Starting sync")
        perf_test_id = '1a26d2ae-2111-11ec-ad23-0a6873ed8f5d'
        try:
            self.sync_perf_test(perf_test_id)
            print("synced")
        except:
            pass
        sleep(60)

        self.db_connect()

    def sync_perf_test(self, perf_test_id):
        api_endpoint = "https://api-dev.headspin.io/v0/perftests/{}/dbsync".format(perf_test_id)
        r = requests.post(url=api_endpoint, headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        result = r.json()
        print(r.text)

    def db_connect(self):

        db_config = six.moves.configparser.RawConfigParser()
        db_config.read('db.properties')
        self.db = {}
        self.db['user'] = db_config.get('DB_Config', 'username')
        self.db['pass'] = db_config.get('DB_Config', 'password')
        self.db['name'] = db_config.get('DB_Config', 'database')
        self.db['host'] = db_config.get('DB_Config', 'host')
        self.db['port'] = db_config.get('DB_Config', 'port')

        self.session_id = str(self.session_id)
        cnx = psycopg2.connect(user=str(self.db['user']), password=str(self.db['pass']), host=str(self.db['host']),
                               database=str(self.db['name']), port=str(self.db['port']))
        cursor = cnx.cursor()
        cursor.execute(
            "select avg(y_value) from session_timeseries_data where session_id = '{}'  AND timeseries_key = 'video_quality_mos' AND x_value between {} and {};".format(
                self.video_start, self.video_end))
        value = cursor.fetchall()
        value = (value[0][0])
        self.video_mos_score = value
        print("video_quality_mos: ", self.video_mos_score)

    def test_login(self):

        self.pic = []
        self.session_id = self.driver.session_id
        api_endpoint = "https://api-dev.headspin.io/v0/sessions/tags/{}".format(self.session_id)
        session_data = [{"session type": "video"}]
        r = requests.post(api_endpoint, headers={'Authorization': 'Bearer {}'.format(self.access_token)},
                          json=session_data)
        print(r.text)
        print("Tag added")

        self.driver.implicitly_wait(7)

        try:
            location_access = self.driver.find_element_by_accessibility_id("Allow While Using App").click()
        except:
            pass

        try:
            new_feature = self.driver.find_element_by_ios_predicate("name =='Continue'")
            new_feature.click()
        except:
            pass

        # switch to video
        self.driver.implicitly_wait(60)
        y = self.driver.find_element_by_accessibility_id("CameraMode")
        y = y.location['y']
        screen_size = self.driver.get_window_size()
        self.screen_width = screen_size['width']
        x = self.screen_width / 2 - self.screen_width / 6

        TouchAction(self.driver).tap(None, x, y, 1).perform()

        # video click
        sleep(3)
        screen_size = self.driver.get_window_size()
        self.screen_width = screen_size['width']
        video = self.driver.find_element_by_accessibility_id("VideoCapture")
        location = video.location
        size = video.size

        self.x_tap = location['x'] + int(size['width'] / 2)
        self.y_tap = location['y'] + int(size['height'] / 2)
        TouchAction(self.driver).tap(None, self.x_tap, self.y_tap, 1).perform()
        self.video_start = (float(time.time()) * 1000 - self.start - 10000)
        print(self.video_start)

        folder = str(self.driver.session_id)

        os.mkdir(folder)

        # screen capture thing
        t_end = time.time() + 30

        self.driver.implicitly_wait(1)

        while time.time() < t_end:
            try:
                name = str(time.time())
                name = name + ".png"

                # saving to pic folder
                self.pic.append(name)
                self.driver.save_screenshot(folder + "/" + name)
                print("taking screenshot...")
                sleep(5)
                self.status = "Pass"

            except Exception as e:
                print(e)
                sleep(5)

        TouchAction(self.driver).tap(None, self.x_tap, self.y_tap, 1).perform()
        self.video_end = (float(time.time() * 1000) - self.start - 10000)
        print(self.video_start)

        print("...Images...")
        print(self.pic)

        for img in self.pic:
            print("Analysing:::", folder + "/" + img)
            result = os.system("python3 match.py --template temp.png --images {}".format(folder + "/" + img))
            # result.stdout.read()
        print("Pass")
        self.status = "Pass"


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)






