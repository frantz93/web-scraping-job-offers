#First, we load the required libraries

from cgitb import text
from dataclasses import replace
from gettext import gettext
from msilib.schema import Class
from operator import contains, countOf
from os import getcwd, link
from pickle import TRUE
from typing import Mapping
from unittest import result
from xml.dom.minidom import Element
from attr import attr, attrs
from pyparsing import line
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

import pandas as pd

from lxml import etree


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

#here we load the browser and the indeed website
browser=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
browser.get("https://ca.indeed.com/jobs?q=data%20analyst&l=Quebec%20Province")

time.sleep(3)   #this command force the programm to wait 3 seconds so to make sure the hole page has been loaded 
                #before executing the next commands

#this function will return the path to a specific page on indeed
def test(n):
    next_path = f'//a[@aria-label="{n}"]'   #path structure is obtained through the website html inspection
    return next_path

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

#this function inform on the occurence of a specific string in the job description section
def skill_test(x):
    string = sub_soup.find('div', attrs={'id':'jobDescriptionText'}).text
    result_list = []
    for each in x:        
        result_list.append(each in string)  # append True/False for each element in substring
    r = any(result_list) #call any() with boolean results list
    if r == True:
        result = 'yes'
    else:
        result = 'no'
    return result

#next lines allow to navigates through all the pages containing job announcement
i = 0
page = 1
url = 'https://ca.indeed.com/jobs?q=data%20analyst&l=Quebec%20Province'

jobtab = pd.DataFrame(columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA'])

#report data from web pages to table
while i == 0:

    main_url = url + end_url(page)
    main_soup = BeautifulSoup(getHTML(main_url), "html.parser")
    
    #these command lines may be used to get the total number of job href on a specific page
    #num = 0
    #for each in main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}):
    #    num = num + 1
    #num

    for each in main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}):
        sub_url = 'https://ca.indeed.com' + each['href']
        sub_soup = BeautifulSoup(getHTML(sub_url), "html.parser")
        time.sleep(2)
        dom = etree.HTML(str(sub_soup))
        time.sleep(2)
        #all commands to report data from web pages to table will be there
        #sub_soup = BeautifulSoup(getHTML('https://ca.indeed.com/viewjob?jk=d441350bc37c0f0f&tk=1g8gsuebnkoh7802&from=serp&vjs=3&advn=6781381351210116&adid=385033229&ad=-6NYlbfkN0AmeoOzMpFeQa4nQauBOkgcasiRGbz5T5YfctgmEyRynu_B7G8R18zY3QvB_OzxzaY3yyiQ7FsaOISXGcKdP7Sdb0zQD5paSCg5VZ9NrylfB-VeAZOe1qI2WAyu9d8CY98-ddxRqFa5ktFLYLkCs-N6NsGMJNMQTHHivD3D8VewI8oP_4OZ9oGhAjO2wGu0Amxn-csSve8XBrqV3CYzW1MAkcHr-NTpxXQTq3gfxFJ9U60tHps2-v7LjwE2t-xBx6gGJ8RelwXJ4nwcoH9DoSGez9Xu4DSyAJ4MLgtK52OeXWJFv5rMzTHgrL7xZ2aTkRp8ktj5Y2jqYgMSHS6T45pCF7RlWKla-RYfsUt1vsJAbHZeQslEYmMv&sjdu=9nrDNPdV1DghkDNnC2WJlW1nrk21-asFvjSk9jx-s_PLFBd88MMq2RphcBNLzZL8ANi7xzmMM98sKAS6e6UXGXsXz33hDQmoRdZsP3Oj0-csdU5LpWN0jxJTd7PMdyk_6RWWnthwO9obj2EY-ejpKp0ISMmTCPVnUpO1qfUHDapFg3uikRP50wodwhahAa3a4W3ywYYhd0gishNIvWGYVwNKgh7ZzNLwhHwj-pdjKDcI1Uu2unnsynKiS0GyXbDpYLShhFwgnTAIkcJAonCVV1RyCag4fH0hRj7VkqlSHeeWjRGbOqzPNsuaUO4sad-_hAr6kCfDQEUFQlJSwBsSjFDminH9LTrxZpwCJWJ1504d6t2Ca_8hDP9BSw1Qxgug'), "html.parser")
        #dom = etree.HTML(str(sub_soup))

        title = ''
        comp_name = ''
        location = ''
        t_work = ''
        t_contract =''
        salary = ''

        try:
            title = sub_soup.find('h1').text     #title of the post
        except: pass
        #sub_soup.find_all('h1')[0].text    #title of the post(other command)
        #sub_soup.select('h1')[0].text   #title of the post(other command)

        try:
            comp_name = sub_soup.find('div', attrs={'class':'jobsearch-CompanyReview--heading'}).text      #name of the company
        except: pass
        #sub_soup.select('div.jobsearch-CompanyReview--heading')[0].text     #name of the company (other command)

        try:
            location = dom.xpath('//div[@class="icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle"]//div[contains(text(),"QC")]')[0].text.replace(', QC','')
        except: pass
        #location = sub_soup.find('div', attrs='icl-Ratings-count').findNext('div').text.replace(', QC','')    #location of the job

        #location.xpath('(.//following-sibling::div)[1]')
        
        try:
            t_work = dom.xpath('//div[@class="icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle"]//div[contains(text(),"QC")]/../following-sibling::div/div')[0].text
        except: pass
            
        #t_work = sub_soup.find('div', attrs='icl-Ratings-count').findAllNext('div')[2].text  #type of working (remote or present)

        try:
            t_contract = sub_soup.find('span', attrs={'class':'jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs'}).text      #type of contract (full time/part time, casual/permanent)
        except: pass
        #sub_soup.find('div', attrs={'id':'salaryInfoAndJobType'}).findAll('span')[1].text     #type of contract(other command)
        
        try:
            salary = sub_soup.find('span', attrs={'class':'icl-u-xs-mr--xs attribute_snippet'}).text      #salary
        except: pass

        excel = skill_test(['Excel', 'excel', 'EXCEL'])   #check if SAS skill is required
        python = skill_test(['Python', 'python', 'PYTHON'])   #check if SAS skill is required
        r = skill_test(['R,'])   #check if R skill is required
        sas = skill_test(['SAS'])   #check if SAS skill is required
        stata = skill_test(['Stata', 'stata', 'STATA'])   #check if SAS skill is required
        vba = skill_test(['VBA'])   #check if SAS skill is required

                                                        #set the new line of observation       
        obs = pd.DataFrame([[title, comp_name, location, t_work, t_contract, salary, excel, python, r, sas, stata, vba]], columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA'])
        
        jobtab = pd.concat([jobtab, obs], axis=0)       #adding the new observation to the table
        #jobtab = jobtab.append(obs)                     #other command possible (but will be deprecated soon)  
    
    print(jobtab)

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