#!/usr/bin/env python3

'''
Websites:
    https://www.megacartoons.net
    TODO: https://kimcartoon.li
        document.getElementById("keyword") - input for searching
        document.getElementById("imgSearch") - search button
        document.getElementsByClassName("item")[0].childNodes[1].click() - clickable item link after search
        document.getElementsByClassName("listing")[0].rows - table rows after clicking (first 2 rows are not options)
        document.getElementById("my_video_1") - video
        document.getElementsByClassName("ign") - buttons for previous and next video

Available cartoons in https://www.megacartoons.net:
    Batman Beyond
    Ben 10
    Ben 10: Alien Force
    Ben 10: Ultimate Alien
    Courage the Cowardly Dog
    Cow and Chicken
    Dexter's Laboratory
    Foster's Home for Imaginary Friends
    I Am Weasel
    Johnny Bravo
    Samurai Jack
    Scooby-Doo! Mystery Incorporated
    SpongeBob SquarePants
    The Avengers: Earth's Mightiest Heroes
    The Powerpuff Girls
    The Spectacular Spider-Man
'''

import sys
from select import select
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CHROME_DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
CARTOONS_DROPDOWN_BUTTONS = "menu-link sub-menu-link"
CARTOONS_LIST_BUTTONS = "btn btn-sm btn-default"
VIDEO = 'document.getElementsByTagName("video")[0]'


class CartoonsWatcher():
    def __init__(self):
        # Driver configuration
        self.options = Options()
        self.options.add_argument("start-maximized")

        # Disable '[Browser] is being controlled by automated test software' message, NOT WORKING
        self.options.add_argument('disable-infobars')
        self.options.add_extension(
            "/home/pi/.config/chromium/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.51.0_0.crx")  # uBlock Origin
        self.options.add_extension(
            "/home/pi/.config/chromium/Default/Extensions/aleakchihdccplidncghkekgioiakgal/1.1.0_0.crx")  # h264ify

        # Initialize the driver
        self.driver = webdriver.Chrome(service=Service(
            CHROME_DRIVER_PATH), options=self.options)
        self.driver.set_page_load_timeout(15)
        print("Opening browser, please wait")
        self.driver.get("https://www.megacartoons.net")

        print("The available cartoons are:")
        self.get_cartoons_list()

        try:
            cartoon_num = int(input("Enter cartoon number: "))

            if cartoon_num > len(self.cartoons_list) or cartoon_num < 1:
                raise ValueError

            cartoon_num -= 1
        except:
            print(
                f"Invalid input! Enter a number between 1 and {len(self.cartoons_list)}!")
            exit()

        self.cartoon_num = cartoon_num
        self.curr_ep = 1

    def get_cartoons_list(self):
        cartoons_list = (self.driver.execute_script(
            f'let list = document.getElementsByClassName("{CARTOONS_DROPDOWN_BUTTONS}"); \
            let newList = []; Array.prototype.map.call(list, v => {{ newList.push(v.innerText) }}); return newList'))

        for i, c in enumerate(cartoons_list):  # List available cartoons
            print("{:2}. {}".format(i + 1, c))

        self.cartoons_list = cartoons_list

    def play_video(self):
        play_btn = 'document.getElementsByClassName("fp-play")[0]'
        fs_btn = 'document.getElementsByClassName("fp-fullscreen fp-icon")[0]'

        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(
                Keys.SPACE)  # Fix for Chrome autoplay policy
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fp-volume a")))
            # Click the div above the video
            self.driver.execute_script(f'{play_btn}.click()')
            print("Loading episode")

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, "video")))
            while self.driver.execute_script(f'return document.fullscreenElement != {VIDEO}.parentElement'):
                self.driver.execute_script(
                    f'{fs_btn}.click()')  # Set full screen
        except JavascriptException:
            print("JavaScript error occured!")
        except:
            print("Time out exception")
            self.driver.quit()
            exit()

    def run(self):  # Main function
        self.select_episode()
        self.start_episode()
        inp = ''
        print("==================")
        has_exception_occured = False

        while not inp.startswith('q'):
            ready, _, _ = select([sys.stdin], [], [], 1)

            if ready:
                inp = sys.stdin.readline().rstrip('\n')
                sys.stdout.flush()

            if inp.startswith('p'):
                self.toggle_play_pause()

            if not has_exception_occured:
                try:
                    # Start next episode
                    if self.driver.execute_script(f'return {VIDEO}.currentTime == {VIDEO}.duration'):
                        self.curr_ep += 1
                        self.driver.execute_script(
                            f'alert("Starting episode {self.curr_ep + 1}")')  # Notification alert
                        sleep(3)
                        self.driver.switch_to.alert.accept()  # Close the alert
                        self.start_episode()
                except JavascriptException:
                    has_exception_occured = True
                    print("Autoplay disabled due to manual user interaction")

            sleep(1)

        self.driver.quit()

    def select_episode(self):
        print(f"Finding cartoon {self.cartoons_list[self.cartoon_num]}")

        # Select cartoon from the dropdown with available ones
        self.driver.execute_script(
            f'document.getElementsByClassName("{CARTOONS_DROPDOWN_BUTTONS}")[{self.cartoon_num}].click()')
        self.driver.execute_script(
            'document.getElementsByClassName("link-overlay fa fa-play")[0].click()')  # Open the first available episode (last uploaded)
        ep_count = self.driver.execute_script(
            f'return document.getElementsByClassName("{CARTOONS_LIST_BUTTONS}").length')  # Get episodes count

        try:
            selected_ep = int(input(f"Which episode (1-{ep_count}): "))
        except:
            print(f"Invalid input! Enter a number between 1 and {ep_count}!")
            self.driver.quit()
            exit()

        self.curr_ep = selected_ep - 1

    def start_episode(self):
        # Start requested episode
        print(f'Starting episode {self.curr_ep + 1}')
        self.driver.execute_script(
            f'document.getElementsByClassName("{CARTOONS_LIST_BUTTONS}")[{self.curr_ep}].click()')
        self.play_video()

    def toggle_play_pause(self):
        self.driver.execute_script(
            'document.getElementsByClassName("fp-engine intrinsic-ignore")[0].click()')  # Start or pause the video


if __name__ == "__main__":
    cartoons_watcher = CartoonsWatcher()
    cartoons_watcher.run()
