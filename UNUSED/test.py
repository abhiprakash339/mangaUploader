import time
import gc
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

chromeOptions = webdriver.ChromeOptions()
chromeOptions.set_headless()
# self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fireFoxOptions)
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)

url = 'https://manga4life.com/read-online/Jujutsu-Kaisen-chapter-144-page-1.html'
# url = 'https://manga4life.com/read-online/Jujutsu-Kaisen-chapter-144-page-1.html'
page = 1
driver.get(url)
gc.collect()
if "404 Page Not Found" == driver.title:
    print('ERROR')
    exit(0)
# time.sleep(10)
print('SUC')
w = WebDriverWait(driver, 10)
gc.collect()
w.until(EC.visibility_of_element_located(
    (By.XPATH, '//*[@id="TopPage"]/div[2]/div/img')))  # //*[@id="TopPage"]/div[2]/div/img
print('kkkk')
print(driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div/img').get_attribute("ng-src"))
