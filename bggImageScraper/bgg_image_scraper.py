import argparse
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (InvalidArgumentException,
                                        TimeoutException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USER_AGENT = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"


class ImageScrapper:
    def __init__(self, url_list: str):
        self.url_list = url_list
        self.options = webdriver.FirefoxOptions()
        self.options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        self.options.add_argument("--headless")
        self.options.add_argument(USER_AGENT)
        self.driver = webdriver.Firefox(service=Service(
            r"C:\Program Files\Mozilla Firefox\geckodriver.exe"), options=self.options)

    def get_board_game_image(self):
        try:
            with open(self.url_list, 'r') as f:
                for line in f.readlines():
                    if line.startswith("https://boardgamegeek.com/boardgame"):
                        self._find_image(line)
                        time.sleep(1)
                    else:
                        print(f"Invalid URL: {line}\nExiting")
                        exit(1)
        except FileNotFoundError:
            print(f"Could not open \"{self.url_list}\". File not found!")
            exit(1)

    def _find_image(self, url: str):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "game-year"))
            )
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            s = soup.find("img", class_="img-responsive")
            img_url = s["src"]
            s = soup.find(
                "span", class_="game-year").find_previous_sibling("a").find("span")
            bg_name = s.get_text()
            self._save_image(img_url, bg_name)
        except InvalidArgumentException:
            print(f"Invalid URL \"{url}Exiting\"")
            exit(1)
        except TimeoutException:
            print(
                f"{url} timed out\nCheck your Internet connection\nMake sure to provide a valid BGG game link")
            exit(1)

    def _edit_invalid_chars(self, s: str) -> str:
        s = list(s)
        for i, x in enumerate(s):
            if x == ':':
                s[i] = ' -'

        return ''.join(s)

    def _save_image(self, url: str, name: str):
        r = requests.get(url)
        name = self._edit_invalid_chars(name) + ".png"

        try:
            with open(name, 'wb') as f:
                f.write(r.content)
            print(f"Saved \"{name}\"")
        except:
            print("An error occured while saving")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Board Games Image Scraper from BGG")
    parser.add_argument("urls", help="Provide a text file containing BGG URLs")
    args = parser.parse_args()

    ims = ImageScrapper(args.urls)
    ims.get_board_game_image()
