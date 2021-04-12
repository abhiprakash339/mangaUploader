import threading

from PIL import Image
from selenium import webdriver
from pymongo import MongoClient
from PyPDF2 import PdfFileMerger
from configparser import ConfigParser
from requests.adapters import HTTPAdapter
# from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flask import Flask, request, send_from_directory
from flask_restful import Api, Resource

chromeOptions = webdriver.ChromeOptions()
chromeOptions.set_headless(headless=True)
print(chromeOptions.headless)
# self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fireFoxOptions)
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
import os, psutil


class Test:
    global driver

    def __init__(self):
        pass

    def title(self, URL):
        while True:
            driver.get(URL)
            print(driver.title)
            driver.quit()

    def start(self):
        t = threading.Thread(target=self.title, args=('https://google.com',), name='TITLE')
        t.start()


obj = Test()
obj.start()
