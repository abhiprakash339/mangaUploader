from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

fireFoxOptions = webdriver.ChromeOptions()
fireFoxOptions.set_headless()
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=fireFoxOptions)