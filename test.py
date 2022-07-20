#First, we load the required libraries

from cgitb import text
from dataclasses import replace
from msilib.schema import Class
from operator import contains, countOf
from os import getcwd, link
from xml.dom.minidom import Element
#import pwd
#from re import U
#from tkinter import Button
#from unicodedata import name
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import shutil


#-----------------------------------------------------------#
#---Programm command lines for web scraping on LindkedIn----#
#-----------------------------------------------------------#

browser=webdriver.Chrome(ChromeDriverManager().install())
#browser=webdriver.Chrome(executable_path='C:/Users/user/Desktop/github/web-scraping-job-offers/chromedriver.exe')
browser.get("https://www.linkedin.com/jobs/search?keywords=data%2Banalyst&location=Quebec")
time.sleep(5)
#browser.find_element(By.XPATH,"/html/body/div[1]/header/nav/div/a[2]").click()
browser.find_element(By.XPATH,"//*[@class='nav__button-secondary btn-md btn-secondary-emphasis']").click()
browser.find_element(By.XPATH, "//*[@class='btn-text']").click()
#Calculate the number of pages to load
nb = int(browser.find_element(By.CLASS_NAME, 'results-context-header__job-count').text.replace("/u202f",''))
nb_pages = int(nb/25) + round(nb/25 % 1)
if nb_pages > 6:
    i = 1
    while i < 7:
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        i = i + 1
        time.sleep(3)
    while i < nb_pages:
        button = browser.find_element(By.XPATH, '//*[@id="main-content"]/section[2]/button')
        button.click()
        time.sleep(3)
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        i = i + 1
        time.sleep(3)
else:
    while i < nb_pages:
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        i = i + 1
        time.sleep(3)


button = browser.find_element(By.LINK_TEXT,"Data Analyst")

button = browser.find_element(By.XPATH, '//*[@id="jserp-filters"]/ul/li[6]/div/div/button')

nb.get_attribute('innerHTML')
WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='S'inscrire']"))).click()

browser.close()


#--------------------------------------------------------#
#---Programm command lines for web scraping on Indeed----#
#--------------------------------------------------------#

#this function will return the path to a specific page on indeed
def test(n):
    next_path = f'//a[@aria-label="{n}"]'   #path structure is obtained through the website html inspection
    return next_path

#here we load the browser and the indeed website
browser=webdriver.Chrome(ChromeDriverManager().install())
browser.get("https://ca.indeed.com/jobs?q=data%20analyst&l=Quebec%20Province")

time.sleep(3)   #this command force the programm to wait 3 seconds so to make sure the hole page has been loaded 
                #before executing the next commands

#this function return the end of url for each page
def end_url(x):
    if x > 1:
        a = x - 1
        end = 'start=' + f'{a}0'
    else:
        end = ""       #first page has no ending
    return end

# function to extract html document from given url
def getHTML(url):
    # request for HTML document of given url
    response = requests.get(url)
    # response will be provided in JSON format
    return response.text

#next lines allow to navigates through all the pages containing job announcement
i = 0
page = 1
main_url = 'https://ca.indeed.com/jobs?q=data%20analyst&l=Quebec%20Province'



while i == 0:
    #report data from web pages to table
    
    main_soup = BeautifulSoup(getHTML(main_url), "html.parser")
    
    #these command lines may be used to get the total number of job href on a specific page
    #num = 0
    #for each in main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}):
    #    num = num + 1
    #num

    for each in main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}):
        sub_url = 'https://ca.indeed.com' + each['href']
        sub_soup = BeautifulSoup(getHTML(sub_url), "html.parser")
        #all commands to report data from web pages to table will be there




    link = main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'})[0]['href']
    sub_url = 'https://ca.indeed.com' + link

    
    
    try:
        page = page + 1
        browser.find_element(By.XPATH, test(page)).click()     #change to next page
        time.sleep(2)
        if page == 2:
            browser.find_element(By.XPATH, '//*[@id="popover-x"]/button').click()       #close popup window
        browser.execute_script("window.scrollTo(0,5000)")
    except NoSuchElementException:
        i = 1



i = 1
while i < 14:
    browser.execute_script("window.scrollTo(0,5000)")
    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="resultsCol"]/nav/div/ul/li[6]/a/span').click()
    time.sleep(2)
    browser.find_element(By.XPATH, '//*[@id="popover-x"]/button').click()



    browser.find_elements(By.CLASS_NAME, 'jobTitle jobTitle-newJob css-bdjp2m eu4oa1w0')        #find all new jobs
    browser.find_elements(By.CLASS_NAME, 'jobTitle css-1h4a4n5 eu4oa1w0')          #find all old jobs
    browser.find_elements(By.CLASS_NAME, 'jcs-JobTitle css-jspxzf eu4oa1w0')        #find all job titles