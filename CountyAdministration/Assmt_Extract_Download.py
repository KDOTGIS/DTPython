# ---------------------------------------------------------------------------
# Assmnt_Extract_Download.py
# Author: Dirk
# Created on: 2014-02-11
# Description: This script moves the previously downloaded 
# AssmtExtract.csv file to the 
# C:\GISdata\Maintenance\Daily_Extracts\Previous folder, then 
# downloads a new version and places it in the 
# C:\GISdata\Maintenance\Daily_Extracts\Current folder.
# Updated: 2015-01-14
# ---------------------------------------------------------------------------

import os
import shutil
import time
from selenium import webdriver
import datetime

from Assmt_Extract_Config.py import userName, passPhrase, extractURI


def extractDownload():
	try:
	  
		# Set local variables
		Extract_Folder = "C:\\GISdata\\Maintenance\\Daily_Extracts\\Current\\"
		Extract_Source = "C:\\GISdata\\Maintenance\\Daily_Extracts\\Current\\AssmtExtract.csv"
		Extract_Source_Part = "C:\\GISdata\\Maintenance\\Daily_Extracts\\Current\\AssmtExtract.crdownload"
		Extract_Destination = "C:\\GISdata\\Maintenance\\Daily_Extracts\\Previous\\AssmtExtract.csv"
		Chrome_Settings_Path = r"C:\GISdata\Maintenance\Daily_Extracts\Chrome_Settings"
		
		# Check to see if there is an Extract file in the Current folder, then copy it to the Previous
		# folder or print a message saying that there was no file in the current Folder and copying was
		# not attempted.
		if (os.path.isfile(Extract_Source)):
			# Copy the AssmtExtract.csv file, overwriting the file (if any) in the 
			# Daily_Extracts\Previous folder.
			shutil.copy2(Extract_Source, Extract_Destination)
			print "Copied AssmtExtract.csv from the Daily_Extracts\Current to the Daily_Extracts\Previous folder."
			os.remove(Extract_Source)
			print "Removed AssmtExtract.csv from the Daily_Extracts\Current folder."

		else:
			print "Could not find AssmtExtract.csv in the Daily_Extracts\Current folder."
			print "Will not attempt to copy."
			print "Continuing happily."
			
		# The next part sets the Chrome options to use a
		# consistent profile for this script.
		# That's the only way I've found to get Chrome
		# to download to the correct place when it's used
		# with Selenium's webdriver.
		# Having it save the correct download place
		# is easy when it's not used with webdriver, but with
		# webdriver, it's more difficult. So this workaround
		# addresses the webdriver download location.
		
		chromeMods = webdriver.ChromeOptions()
		chromeMods.add_argument("--user-data-dir=" + Chrome_Settings_Path)
		
		# Open the browser with Selenium's Webdriver & ChromeDriver.
		browser = webdriver.Chrome(chrome_options=chromeMods)
		
		#Wait for the browser to load.
		time.sleep(10)
		
		# Then, connect to https://orion7.kdor.org/kdor_mgcentral_crs/login.aspx using
		# selenium's webdriver, ChromeDriver, and Chrome.
		browser.get(extractURI)
		# Make sure that you use HTTPS and not HTTP. With HTTP, the username/password
		# information is sent in plain text. This is not good. HTTPS encrypts the data,
		# which is better.

		# Give the page a chance to load.
		time.sleep(5)

		# Login to the website.
		UserElement = browser.find_element_by_name("txtUserName")
		PassElement = browser.find_element_by_name("txtPassword")
		UserElement.send_keys(userName)
		time.sleep(1)
		PassElement.send_keys(passPhrase)
		time.sleep(1)
		browser.find_element_by_name("btnLogin").click()

		# Alert the user and wait for more loading.
		print "Waiting for the page to load..."
		time.sleep(5)

		# Navigate to the Assessment Extract page.
		browser.find_element_by_link_text("CRS Extracts").click()
		print "Waiting for the next page to load..."
		time.sleep(5)

		# Clear the Ad Hoc Tax Year
		browser.find_element_by_id("ctl00_ContentPlaceHolder1_txtYear").clear()
		
		time.sleep(2)

		# Logic to get the month/year and figure out what year
		# should go in the Ad Hoc Tax Year field.
		try:
			todaysDate = datetime.datetime.now()
			thisYear = int(str(todaysDate.year))
			print "This year = " + str(thisYear)
			thisMonth = int(str(todaysDate.month))
			print "This month = " + str(thisMonth)
			if thisMonth >= 5:
				selectedYear = str(thisYear + 1)
			else:
				selectedYear = str(thisYear)
			print "Selected " + selectedYear + " for the extract year."
		# Will default to 2015 if something goes wrong with the try block above.
		except:
			print "Defaulting to 2015 for the extract year."
			selectedYear = "2015"
		
		browser.find_element_by_id("ctl00_ContentPlaceHolder1_txtYear").send_keys(selectedYear)

		# Select the CSV File radio button in data presentation options.
		# It's selected by default, but it doesn't hurt to be sure.
		browser.find_element_by_id("ctl00_ContentPlaceHolder1_rbOutput_0").click()
		time.sleep(1)
		
		# Then, activate the AssmtExtract link.
		browser.find_element_by_link_text("AssmtExtract").click()

		# Make it wait for up to 20 minutes before closing the browser
		# Check for AssmtExtract.csv
		# Check for AssmtExtract.csv.part
		# When AssmtExtract.csv exists and AssmtExtract.csv.part no longer does
		# Move to the next step.
		print "Waiting up to 20 minutes for the download to complete..."
		countTimes = 0
		CSVTest = 2
		CSVPartTest = 2
		thisTest = True
		while (thisTest == True):
			if (os.path.isfile(Extract_Source)):
				CSVTest = 1
			if (os.path.isfile(Extract_Source_Part)):
				CSVPartTest = 1
			else:
				CSVPartTest = 0
			if ((CSVTest == 1) and (CSVPartTest == 0) or (countTimes >= 120)):
				thisTest = False
			time.sleep(10)
			countTimes = countTimes + 1
			
		if (countTimes >= 120):
			print "The download may have timed out. Ooops."
		else:
			print "The Assessment Extract should now be up to date."
		
		time.sleep(5)
		
		# Delete the login cookie and close the browser.
		print "Clearing session cookies and closing the browser."
		browser.delete_all_cookies()
		browser.close()
		browser.quit()
	
	except Exception as e:
		# If an error occurred, print line number and error message
		import traceback, sys
		tb = sys.exc_info()[2]
		print "Line %i" % tb.tb_lineno
		print e.message
		
if __name__ == "__main__":
	extractDownload()
	print "Script completed."
	print "Press ENTER or close the script to quit."
	inputTest = raw_input("> ")
	inputTest = inputTest + "a"
	exit()