import copy
import gc
import threading
import time

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

import os, psutil




class Test:
    global driver

    def __init__(self, num):
        self.num = num

    def title(self, URL):
        temp = copy.copy(driver)
        for url in ['https://google.com' for _ in range(10)]:
            time.sleep(1)

            temp.get(url)
            print(temp.title)
            # print('COOKIES :',driver.get_cookies())
            # driver.delete_all_cookies()
            print('ID :',temp.session_id)
            temp.quit()
            # driver.quit()
            # PROCNAME = "chromedriver"#geckodriver"  # or chromedriver or iedriverserver
            # for proc in psutil.process_iter():
            #     # check whether the process name matches
            #     if proc.name() == PROCNAME:
            #         proc.kill()
            self.num += 1
            gc.collect()
        return

    def start(self):
        t = threading.Thread(target=self.title, args=('https://google.com',), name='TITLE')
        t.start()
        # t.join()

    def __del__(self):
        print('Deleting...')


if __name__ == '__main__':
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.set_headless(headless=True)
    # self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fireFoxOptions)
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
    obj = Test(2)
    obj.start()
    while True:
        time.sleep(1)
        print(obj.__dict__)
        print('[INFO] Memory Usage :', psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
