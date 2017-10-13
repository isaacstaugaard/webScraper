import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

source = 'LAX'
destination = 'SFO'
date = '2017-11-02'

driver = webdriver.Chrome()
driver.get("https://skiplagged.com/flights/{0}/{1}/{2}".format(source,destination,date))
driver.maximize_window() #For maximizing window
time.sleep(1)
driver.implicitly_wait(5) #gives an implicit wait for 20 seconds
xpathToInfiniteList = '//*[@id="trip-list-sections"]/div[2]/div[1]/div[5]'

no_of_pagedowns = 2
elem1 = driver.find_element_by_tag_name("body")
while no_of_pagedowns:
	for elem in driver.find_elements_by_xpath(xpathToInfiniteList):  #Xpath to the infinite-trip-list div #Only works properly when the mouse is over the flight section for some reason
		print (elem)
		print(" ------------------------------------------------------------------------------------------------- ")

	elem1.send_keys(Keys.PAGE_DOWN)
	time.sleep(1)  #Time in between scrolls
	no_of_pagedowns-=1

