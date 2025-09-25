from selenium import webdriver
import geckodriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

try:
    geckodriver_autoinstaller.install()
except:
    print("check driver, do you have firefox installed?")

#Setter opp tilkoblingen til webdriver
options = webdriver.FirefoxOptions()
#options.add_argument("--log-level=3")
options.add_argument("--no-sandbox")
#options.add_argument("--headless")
#options.add_argument('--width=2560')
#options.add_argument('--height=1440')
driver = webdriver.Firefox(options=options)
driver.maximize_window()
actions = ActionChains(driver)

#Set constants 
timeout = 40
URL = ...


driver.get(URL)#the url you want to go to

#Here you find a html element with by it name, you can use id or any other element that is not dynamic, and then click to execute action
swipe = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(("xpath", '//*[@name="logLogin$AzureLoginButton"]'))) 
swipe.click()

#If you need to use keyboard inputs not directly at the html do it like this
actions.send_keys("g").perform()
actions.send_keys(Keys.ENTER).perform()


#Always at the bottom to not brick your computer 
driver.quit()
