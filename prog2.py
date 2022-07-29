from cgitb import text
from dataclasses import replace
from gettext import gettext
from msilib.schema import Class
from operator import contains, countOf
from os import getcwd, link, stat
from pickle import TRUE
from typing import Mapping
from unittest import result
from xml.dom.minidom import Element
from attr import attr, attrs
from pyparsing import line

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

from tkinter import *
from tkinter import filedialog


#PROG-----------------

input_name.config(state='disabled')
input_place.config(state='disabled')
search_b.config(state='disabled')

file_path = filedialog.askdirectory()

search_name = input_name.get()   #save the job title the user wants to search for
search_place = input_place.get()        #save the job location the user wants to search for

#here we load the browser and the indeed website
browser=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
browser.minimize_window()
browser.get("https://ca.indeed.com/")
time.sleep(2)   #this command force the programm to wait 2 seconds to make sure the hole page has been loaded 
                #before executing the next commands

#clear the search boxes (job title and location) on the web page
browser.find_element(By.ID, 'text-input-what').click()
try: browser.find_element(By.XPATH, '//input[@ID="text-input-what"]/following::span').click()
except: pass
browser.find_element(By.ID, 'text-input-where').click()
try: browser.find_element(By.XPATH, '//input[@ID="text-input-where"]/following::span').click()
except: pass

#search according to the user preferences of job and location
browser.find_element(By.ID, 'text-input-what').send_keys(search_name)      #paste the job title to the box
browser.find_element(By.ID, 'text-input-where').send_keys(search_place)     #paste the job location to the box
browser.find_element(By.XPATH, '//button[@class="yosegi-InlineWhatWhere-primaryButton"]').click()   #search for the results
time.sleep(2)


#now we define useful functions

#this function will return the path to a specific page on indeed

# this function estimates the time necessary for downloading data
def delay(nb):
    t = nb * 3      #total time in seconds (about 3 seconds per page)
    if t/60 < 1:
        delay = f'{t} sec'
    elif t/60 >= 1 and t/3600 < 1:
        delay = f'{int(t/60)} min {round((t/60 - int(t/60))*60)} sec'
    elif t/3600 >= 1 and t/86400 < 1:
        delay = f'{int(t/3600)} hrs {round((t/3600 - int(t/3600))*60)} min'
    else: delay = f'{int(t/86400)} days {int((t/86400 - int(t/86400))*24)} hrs {round(((t/86400 - int(t/86400))*24 - int((t/86400 - int(t/86400))*24))*60)} mns'
    return delay

#this function inform on the occurence of a specific string in the job description section
def skill_test(x):
    result = 'check website'
    try:
        string = browser.find_element(By.XPATH, '//div[@id="jobDescriptionText"]').text
        result_list = []
        for each in x:        
            result_list.append(each in string)  # append True/False for each element in substring
        r = any(result_list) #call any() with boolean results list
        if r == True:
            result = 'yes'
        else:
            result = 'no'
    except: pass
    return result

def test_state(x):
    states = ''
    for each in x[:-1]:
        states = states + f'contains(text(), "{each}") or '
    states = states + f'contains(text(), "{x[-1]}")'
    return states

can_states = ["AB", "BC", "PE", "MB", "NB", "NS", "NU", "ON", "QC", "SK", "NL", "NT", "YT"]


#next lines allow to navigates through all the pages containing job announcement and store relevant data in a dataframe

jobtab = pd.DataFrame(columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA', 'SQL', 'POWER_BI', 'WEBSITE'])

#collecting the jobs' access links
links = []
i = 0
while i == 0:
    for each in browser.find_elements(By.XPATH, '//a[@class="jcs-JobTitle css-jspxzf eu4oa1w0"]'):
        links.append(each.get_attribute('href'))
    try:
        main_url = browser.find_element(By.XPATH, '//head/link[@rel="next"]').get_attribute('href')
        browser.get(main_url)
        time.sleep(2)
    except NoSuchElementException:
        i = 1

print(f'Data on {len(links)} jobs will be downloaded. Estimated time is {delay(len(links))}.')

#downloading data on the jobs
id = 0
for each in links:
    browser.get(each)
    time.sleep(2)

    #Commands to report data from web pages to database
    id = id + 1
    title = ''
    comp_name = ''
    location = ''
    t_work = ''
    t_contract =''
    salary = ''
    website = ''

    try:
        title = browser.find_element(By.XPATH, '//h1').text     #title of the post
    except: pass

    try:
        comp_name = browser.find_element(By.XPATH, '//div[contains(@class,"jobsearch-InlineCompanyRating")]//a').text    #name of the company
    except: pass

    try:
        location = browser.find_element(By.XPATH, f'//div[contains(@class,"jobsearch-JobInfoHeader-subtitle")]//div[{test_state(can_states)}]').text     #location of the job
    except: pass
    
    try:
        t_work = browser.find_element(By.XPATH, f'//div[contains(@class,"jobsearch-JobInfoHeader-subtitle")]//div[{test_state(can_states)}]/following::div').text   #type of work (remote, hybride)
    except: pass

    try:
        t_contract = browser.find_element(By.XPATH, '//span[contains(@class,"jobsearch-JobMetadataHeader")]').text      #type of contract (full time/part time, casual/permanent)
    except: pass
    
    try:
        salary = browser.find_element(By.XPATH, '//span[@class="icl-u-xs-mr--xs attribute_snippet"]').text      #salary
    except: pass

    excel = skill_test(['Excel', 'excel', 'EXCEL', 'MSExcel', 'MSexcel'])   #check if SAS skill is required
    python = skill_test(['Python', 'python', 'PYTHON'])   #check if SAS skill is required
    r = skill_test(['R,', 'R.', 'R)'])   #check if R skill is required
    sas = skill_test(['SAS'])   #check if SAS skill is required
    stata = skill_test(['Stata', 'stata', 'STATA'])   #check if SAS skill is required
    vba = skill_test(['VBA'])   #check if SAS skill is required
    sql = skill_test(['SQL'])   #check if SQL skill is required
    power_bi = skill_test(['Power BI', 'PowerBI', 'powerBI', 'power BI', 'BI visualization'])       #check if Power BI skill is required

    website = each
                                                    #set the new line of observation       
    obs = pd.DataFrame([[title, comp_name, location, t_work, t_contract, salary, excel, python, r, sas, stata, vba, sql, power_bi, website]], columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA', 'SQL', 'POWER_BI', 'WEBSITE'])
    
    jobtab = pd.concat([jobtab, obs], axis=0)       #adding the new observation to the table

print(f'{id} jobs were found that meet your caracteristics')

print(jobtab)

browser.close()

jobtab.to_csv(file_path + '/jobs.csv', index=False, encoding='UTF-8', sep=';')       #save the database to csv file

input_name.config(state='normal')
input_place.config(state='normal')
search_b.config(state='normal')