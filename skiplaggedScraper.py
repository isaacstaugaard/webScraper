import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
import argparse 												  #Needed to read the args from cmd line 
from lxml import html 
from selenium.webdriver.common.by import By                       #Allows the use of By 
from selenium.webdriver.support.ui import WebDriverWait			  #Allows for the driver to wait for dadta
from selenium.webdriver.common.keys import Keys                   #Allows for scrolling down (PGDOWN key)
from selenium.webdriver.common.action_chains import ActionChains  #Allows for mouseOver


def scrapeWebsite(source,destination,date):
	driver = webdriver.Chrome()
	driver.get("https://skiplagged.com/flights/{0}/{1}/{2}".format(source,destination,date))  #Opens the driver to the correct webpage
	time.sleep(1)  #Let the webpage load before maximizing
	driver.maximize_window() #For maximizing window
	time.sleep(1) #Let the webpage sit until we move the mouse

	#  Move the mouse and change the option for money to US Dollars instead of Canadanian Dollars -- #
	xpathToCurrencyDropdown = '//*[@id="currency-dropdown"]/a'
	xpathToUSDOption = '//*[@id="currency-dropdown"]/ul/li[11]/a/span'
	driver.find_element_by_xpath(xpathToCurrencyDropdown).click()
	time.sleep(.5)
	driver.find_element_by_xpath(xpathToUSDOption).click()
	time.sleep(2)

	# -- Move mouse to hover over the first element on the PAGE_DOWN -- #
	xpathToTripListSections = '//*[@id="trip-list-sections"]/div[2]'
	element = driver.find_element_by_xpath(xpathToTripListSections)
	hov = ActionChains(driver).move_to_element(element)
	hov.perform()
	time.sleep(1)

	# -------- Try to print out all the different attributes from JUST the first element -------- #
	# pathToFirstElemLength = '//*[@id="4d7ded7b19fd4946b25526c94ef76a3634ed8fac852a28bece2368b73ee2800fcd5701ec4aa59898b872713bc8ffe353ecd233c745b206d0e154bc154f4e87f7b50867c321d50a993424cf6f04aca609f6525edcf53a19260513ef4810a586f9"]/div[1]'
	# first =  driver.find_elements_by_xpath(pathToFirstElemLength)
	# hello = first[0].text.split('\n')
	# print(first[0].text)
	# print(hello)

	duration = []
	stops = []
	deptTime = []
	deptAir = []
	arrTime = []
	arrAir = []
	price = []
	flights = []

	xpathToInfiniteList = '//*[@id="trip-list-sections"]/div[2]/div[1]/div[5]'   #string that holds the xpath to the flights section
	no_of_pagedowns = 3		#Number of times we wish to scroll the page down (Need this here to load more flights in)
	elem1 = driver.find_element_by_tag_name("body")   #The element that we will be scrolling down
	while no_of_pagedowns:
		for elem in driver.find_elements_by_xpath(xpathToInfiniteList):  #Xpath to the infinite-trip-list div #Only works properly when the mouse is over the flight section for some reason
			hello = elem.text.split('\n')
			i = 0
			lengthOfHello = len(hello)
			while i < lengthOfHello:
				if (i % 7  == 0):
					duration.append(hello[i])
				if (i%7 == 1):
					stops.append(hello[i])
				if (i%7 == 2):
					deptTime.append(hello[i])	
				if (i%7 == 3):
					deptAir.append(hello[i])	
				if (i%7 == 4):
					arrTime.append(hello[i])	
				if (i%7 == 5):
					arrAir.append(hello[i])	
				if (i%7 == 6):
					price.append(hello[i])																							
				i = i+1
			# -------- Prints all of the elements one by one, one per line -------- #
			#print (elem.text)

		elem1.send_keys(Keys.PAGE_DOWN)
		time.sleep(1)  #Time in between scrolls
		no_of_pagedowns-=1
	
	# -------- These are print functions for each indiviual value -------- #
	#print("Duration: ", duration, "\n")
	#print("Stops: ", stops, "\n")
	#print("Departure Time: ", deptTime, "\n")
	#print("Departure Airport: ", deptAir, "\n")
	#print("Arrival Time: ", arrAir, "\n")
	#print("Arrival Airport: ", arrAir, "\n")
	#print("Price: ", price, "\n")
	k=0
	numElements = len(duration)
	while (k < numElements):
		flights.append( [ duration[k], stops[k], deptTime[k], deptAir[k], arrTime[k], arrAir[k], price[k] ] )
		k += 1
	print("Flights: ", flights)

	time.sleep(5)  #Lets the browser stay open for 5s
	#driver.quit()


if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('source',help = 'Source airport code')
	argparser.add_argument('destination',help = 'Destination airport code')
	argparser.add_argument('date',help = 'YYYY-MM-DD')

	args = argparser.parse_args()
	source = args.source
	destination = args.destination
	date = args.date
	print ("Fetching flight details\n")
	scraped_data = scrapeWebsite(source,destination,date)

