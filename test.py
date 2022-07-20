from cgitb import text
from msilib.schema import Class
from operator import contains
from os import getcwd, link
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

#next lines allow to navigates through all the pages containing job offer annouce
i = 0
page = 2
while i == 0:
    try:
        browser.find_element(By.XPATH, test(page)).click()     #change to next page
        time.sleep(2)
        if page == 2:
            browser.find_element(By.XPATH, '//*[@id="popover-x"]/button').click()       #close popup window
        browser.execute_script("window.scrollTo(0,5000)")
        page = page + 1
    except NoSuchElementException:
        i = 1




i = 1
while i < 14:
    browser.execute_script("window.scrollTo(0,5000)")
    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="resultsCol"]/nav/div/ul/li[6]/a/span').click()
    time.sleep(2)
    browser.find_element(By.XPATH, '//*[@id="popover-x"]/button').click()



