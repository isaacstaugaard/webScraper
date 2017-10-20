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
import smtplib													  #Allows use of email
import psycopg2

conn = psycopg2.connect(database="DATABASE", user = "USER", password = "PASSWORD", host = "127.0.0.1", port = "PORT")
print ("PostgreSQL: Opened database successfully")
cur = conn.cursor()

# ------------------ This is used to create a new table, only needs to be done once ----------------------- #
#cur.execute('''CREATE TABLE FLIGHTDATA
#      (DURATION text,
#      STOPS text, 
#      deptTime text, 
#      deptAir text, 
#      arrTime text, 
#      arrAir text, 
#      price text);''')
#print ("PostgreSQL: Table created successfully")
#conn.commit() 

def scrapeWebsite(source,destination,date):
	driver = webdriver.Chrome()
	driver.get("https://skiplagged.com/flights/{0}/{1}/{2}".format(source,destination,date))  #Opens the driver to the correct webpage
	#time.sleep(1)  #Let the webpage load before maximizing
	driver.maximize_window() #For maximizing window
	time.sleep(1) #Let the webpage sit until we move the mouse

	#  Move the mouse and change the option for money to US Dollars instead of Canadanian Dollars -- #
	xpathToCurrencyDropdown = '//*[@id="currency-dropdown"]/a'
	xpathToUSDOption = '//*[@id="currency-dropdown"]/ul/li[11]/a/span'
	driver.find_element_by_xpath(xpathToCurrencyDropdown).click()
	time.sleep(.5)
	driver.find_element_by_xpath(xpathToUSDOption).click()
	time.sleep(8) #Let the webpage load fully (takes a while for the spirit airlines to show up)

	# -- Move mouse to hover over the first element on the PAGE_DOWN -- #
	xpathToTripListSections = '//*[@id="trip-list-sections"]/div[2]'
	element = driver.find_element_by_xpath(xpathToTripListSections)
	hov = ActionChains(driver).move_to_element(element)
	hov.perform()
	time.sleep(1)

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

		elem1.send_keys(Keys.PAGE_DOWN)
		time.sleep(.5)  #Time in between scrolls
		no_of_pagedowns-=1
	
	k=0
	numElements = len(duration)
	while (k < numElements):
		flights.append( [ duration[k], stops[k], deptTime[k], deptAir[k], arrTime[k], arrAir[k], price[k] ] )
		k += 1
	print("Flights: ", flights, "\n")

	#------------------- DELETE THE DATA CURRENTLY STORED IN FLIGHTDATA ------------------------------------------#
	cur.execute("DELETE FROM FLIGHTDATA")


	#------------------- THIS PUTS THE CURRENT DATA INTO THE SQL TABLE CALLED FLIGHTDATA --------------------------#
	z=0
	while (z < numElements):
		cur.execute("INSERT INTO FLIGHTDATA (DURATION,STOPS,DEPTTIME,DEPTAIR,ARRTIME,ARRAIR,PRICE) \
      		VALUES (%s, %s, %s, %s, %s, %s, %s)", (flights[z][0], flights[z][1], flights[z][2], flights[z][3], flights[z][4], flights[z][5], flights[z][6] ));
		z += 1

	conn.commit()
	print ("PostgreSQL: Records created successfully")
	conn.close()


	lowestPrice = int(price[0].replace("$",""))
	if (lowestPrice <= targetPrice):
		return 'YES'
	else:
		return 'NO'

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
	global targetPrice
	targetPrice = 45
	print ("Fetching flight details\n")
	scraped_data = scrapeWebsite(source,destination,date)


# ---------------------- This is for sending an email when the price is below a certain threshold --------------------- #
	if (scraped_data == 'YES'):
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login("INSERT YOUR EMAIL HERE", "INSERT EMAIL PASSWORD HERE")
		msg = "Flight cheaper than " + str(targetPrice) + " on " + date + "!!!"
		server.sendmail("INSERT YOUR EMAIL", "INSERT TARGET EMAIL", msg)
		server.quit()

