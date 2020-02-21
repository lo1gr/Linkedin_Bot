# /usr/local/bin/python3
"""
	Desc: Bot to crawl onto linkedin and send out invitations to
		  users based on search criteria and message.
"""
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# sound
import subprocess

import numpy as np
from bs4 import BeautifulSoup

# to randomize wait times
import random

from credentials import user, password, message, keyword, sound, connect, job_title_contains, total_count_allowed


#GLOBAL VALUES USED IN SCRIPT
url = "https://www.linkedin.com/uas/login?goback=&trk=hb_signin"
url_2 = 'https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22S%22%5D&keywords=microsoft&origin=FACETED_SEARCH'
base_search_URL = 'https://www.linkedin.com/search/results/people/?keywords='


# SCRAPPER CLASS AND IT'S METHODS
class LinkedInScrapper():

	def __init__(self,username=user,password=password,message=message,search=keyword, sound_on = sound):
		self.driver = webdriver.Chrome(ChromeDriverManager().install())
		self.username = user
		self.password = password
		self.message = message
		self.search = keyword
		self.sound_on = sound
		self.connect = connect
		self.job_title_contains = job_title_contains
		self.total_count_allowed = total_count_allowed
		self.count = 0
		self.page_count = 1

	def Login(self):
		#lets get to the site
		self.driver.get(url)
		time.sleep(2)
		try:
			self.driver.find_element_by_name("session_key").send_keys(self.username)
			self.driver.find_element_by_name("session_password").send_keys(self.password+Keys.RETURN)
			time.sleep(2)	#give some time for the login.
		except Exception as a:
			print(str(a))

	def Search(self):
		#Lets search based on what keywords we chose
		#lets first compose the URL
		self.search_url = base_search_URL
		keywords = self.search.split(' ')
		for word in keywords:
			self.search_url += word + '%20'
		self.search_url += "&origin=GLOBAL_SEARCH_HEADER"	#add the last word and the end parameters
		self.driver.get(self.search_url)

		if self.sound_on:
			subprocess.call(['afplay',"chinese-gong.wav"])

	def send_connection(self, note = True):
		# include if has pending instead of connect
		if self.count == self.total_count_allowed:
			# will exit because will throw an error
			0/0
		try:
			self.driver.find_element_by_xpath("//*[@class='pv-s-profile-actions pv-s-profile-actions--connect ml2 artdeco-button artdeco-button--2 artdeco-button--primary ember-view']").click()
		except NoSuchElementException:
			self.driver.find_element_by_xpath("//*[@class='ml2 pv-s-profile-actions__overflow-toggle artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view']/span").click()
		time.sleep(1)
		try:
			if note == False:
				self.driver.find_element_by_xpath("//button[@aria-label='Send now']").click()
				self.count +=1
			else:
				self.driver.find_element_by_xpath("//button[@aria-label='Add a note']").click()
				time.sleep(1)
				self.driver.find_element_by_name("message").send_keys(self.message)
				time.sleep(1)
				self.driver.find_element_by_xpath("//button[@aria-label='Send invitation']").click()
				self.count+=1
				# if could not find add a note it means that we have already sent an invitation to that person!
		except NoSuchElementException:
			pass

	def send_notes(self):
		#This function queries all the buttons on the page
		#adding notes/invitations to only users who have not connected with you

		# do 2, then scroll down a bit
		time.sleep(3)
		self.driver.refresh()

		for i in range(0, 5):
			# will scroll at each iteration of the for loop so that can load other profiles
			try:
				time.sleep(3)
				scroll_delta = int(i)*140
				self.driver.execute_script("window.scrollBy(0, "+str(scroll_delta) + ")")

				all_names = self.driver.find_elements_by_class_name("actor-name")
				all_names_text = [x.text for x in all_names]


				job_desc = self.driver.find_elements_by_xpath("//span[@dir='ltr']")
				# only select the job titles, otherwise location is also chosen
				job_desc_text = [x.text for x in job_desc][::2]


				if i == 0:
					unchecked = [x.text for x in all_names][:5]
					unchecked_title = [x.text for x in job_desc][::2][:5]

				f = open('results.txt','a')
				f.write('unchecked: ' + str(unchecked) + 'now-job: ' + str(unchecked_title[0].split(' '))   + '\n')

				time.sleep(2)

				if unchecked[0] == 'LinkedIn Member':
					unchecked = unchecked[1:]
					unchecked_title = unchecked_title[1:]
					continue

				if len(self.job_title_contains) > 0:
					if any(job in unchecked_title[0].split(' ') for job in job_title_contains):
						all_names[np.where(np.array(all_names_text) == unchecked[0])[0][0]].click()
						unchecked = unchecked[1:]
						unchecked_title = unchecked_title[1:]
						time.sleep(3)

						if self.connect == True:
							if len(self.message) > 0:
								self.send_connection()
							else:
								self.send_connection(note = False)


						self.driver.execute_script("window.history.go(-1)")
					else:
						unchecked = unchecked[1:]
						unchecked_title = unchecked_title[1:]
						continue
				else:
					all_names[np.where(np.array(all_names_text) == unchecked[0])[0][0]].click()
					unchecked = unchecked[1:]
					unchecked_title = unchecked_title[1:]
					time.sleep(3)

					if self.connect == True:
						if len(self.message) > 0:
							self.send_connection()
						else:
							self.send_connection(note = False)

					self.driver.execute_script("window.history.go(-1)")

			except NoSuchElementException:
				self.send_notes()

		f.write('second for loop'+'\n')

		for i in range(5,10):
			try:
				time.sleep(3)
				scroll_delta = 5 * 170 + (int(i)-5) * 100
				self.driver.execute_script("window.scrollBy(0, "+str(scroll_delta) + ")")

				time.sleep(1)

				all_names = self.driver.find_elements_by_class_name("actor-name")
				all_names_text = [x.text for x in all_names]

				job_desc = self.driver.find_elements_by_xpath("//span[@dir='ltr']")
				# only select the job titles, otherwise location is also chosen
				job_desc_text = [x.text for x in job_desc][::2]

				if i == 5:
					unchecked = [x.text for x in all_names][5:]
					unchecked_title = [x.text for x in job_desc][::2][5:]

				f = open('results.txt','a')
				f.write('iter loop:' + str(i) + 'unchecked: ' + str(unchecked) + '\n')

				time.sleep(2)

				if unchecked[0] == 'LinkedIn Member':
					unchecked = unchecked[1:]
					unchecked_title = unchecked_title[1:]
					continue
				else:
					try:
						all_names[np.where(np.array(all_names_text) == unchecked[0])[0][0]].click()
						unchecked = unchecked[1:]
						unchecked_title = unchecked_title[1:]
					except ElementClickInterceptedException:
						try:
							self.driver.execute_script("window.scrollBy(0, -50)")
							all_names[np.where(np.array(all_names_text) == unchecked[0])[0][0]].click()
							unchecked = unchecked[1:]
							unchecked_title = unchecked_title[1:]
						except:
							self.driver.execute_script("window.scrollBy(0, 80)")
							all_names[np.where(np.array(all_names_text) == unchecked[0])[0][0]].click()
							unchecked = unchecked[1:]
							unchecked_title = unchecked_title[1:]

					time.sleep(3)

					if self.connect == True:
						if len(self.message) > 0:
							self.send_connection()
						else:
							self.send_connection(note = False)

					self.driver.execute_script("window.history.go(-1)")

			except (NoSuchElementException, ElementClickInterceptedException) as error:
				self.send_notes()




	def nextPage(self):
		# Head to the next page
		if self.sound_on:
			subprocess.call(['afplay',"chinese-gong.wav"])
		else:
			time.sleep(2)	#lets wait for page to load

		# page_count shall start at 1
		self.page_count+=1
		self.driver.get(self.search_url + "&page=" + str(self.page_count))


		# too slow:


		# self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		#
		# time.sleep(2)
		# self.driver.find_element_by_xpath("//button[@aria-label='Next']").click()



if __name__ == "__main__":
	#Call the function
	L = LinkedInScrapper()
	L.Login()
	L.Search()
	while True:
		L.send_notes()
		L.nextPage()
