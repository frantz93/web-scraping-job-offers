#--------------------------------------------------------#
#---Programm command lines for web scraping on Indeed----#
#--------------------------------------------------------#

#First, we load the required libraries

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

def search_jobs():

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
    time.sleep(1)


    #now we define useful functions

    #this function will return the path to a specific page on indeed
    def test(n):
        next_path = f'//a[@aria-label="{n}"]'   #path structure is obtained through the website html inspection
        return next_path

    #this function return the end of url for each page
    def end_url(x):
        if x > 1:
            a = x - 1
            end = '&start=' + f'{a}0'
        else:
            end = ""       #first page has no ending
        return end

    # function to extract html document from given url
    def getHTML(url):
        # request for HTML document of given url
        response = requests.get(url, headers={"Content-Type":"text"})
        # response will be provided in JSON format
        return response.text

    # this function estimates the time necessary for downloading data
    def delay(nb):
        if nb/20 < 1:
            delay = f'{int(nb/20)*60} sec'
        elif nb/20 >= 1 and nb/20 < 60:
            delay = f'{int(nb/20)} mns'
        else: delay = f'{int(nb/20/60)} hrs {int(((nb/20/60)-int(nb/20/60))*60)} mns'
        return delay

    #this function inform on the occurence of a specific string in the job description section
    def skill_test(x):
        result = 'check website'
        try:
            string = sub_soup.find('div', attrs={'id':'jobDescriptionText'}).text
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

    #estimate the time for dowloading data
    nb = int(browser.find_element(By.ID, 'searchCountPages').text.split()[3])
    print(f'Data on {nb} jobs will be downloaded. Estimated time is {delay(nb)}.')

    #next lines allow to navigates through all the pages containing job announcement

    i = 0
    main_url = browser.current_url
    jobtab = pd.DataFrame(columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA', 'SQL', 'POWER_BI', 'WEBSITE'])

    while i == 0:

        main_soup = BeautifulSoup(getHTML(main_url), "html.parser")
        
        for each in main_soup.find_all('a', attrs={'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}):
            sub_url = 'https://ca.indeed.com' + each['href']
            sub_soup = BeautifulSoup(getHTML(sub_url), "html.parser")
            time.sleep(1)
            dom = etree.HTML(str(sub_soup))
            time.sleep(1)
            
            #Commands to report data from web pages to database
            title = ''
            comp_name = ''
            location = ''
            t_work = ''
            t_contract =''
            salary = ''
            website = ''

            try:
                title = sub_soup.find('h1').text     #title of the post
            except: pass

            try:
                comp_name = dom.xpath("//div[@class='jobsearch-InlineCompanyRating icl-u-xs-mt--xs jobsearch-DesktopStickyContainer-companyrating']//a")[0].text    #name of the company
            except: pass

            try:
                location = dom.xpath('//div[@class="icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle"]//div[contains(text(),"QC")]')[0].text.replace(', QC','')
            except: pass
            
            try:
                t_work = dom.xpath('//div[@class="icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle"]//div[contains(text(),"QC")]/../following-sibling::div/div')[0].text
            except: pass

            try:
                t_contract = sub_soup.find('span', attrs={'class':'jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs'}).text      #type of contract (full time/part time, casual/permanent)
            except: pass
            
            try:
                salary = sub_soup.find('span', attrs={'class':'icl-u-xs-mr--xs attribute_snippet'}).text      #salary
            except: pass

            excel = skill_test(['Excel', 'excel', 'EXCEL', 'MSExcel', 'MSexcel'])   #check if SAS skill is required
            python = skill_test(['Python', 'python', 'PYTHON'])   #check if SAS skill is required
            r = skill_test(['R,', 'R.', 'R)'])   #check if R skill is required
            sas = skill_test(['SAS'])   #check if SAS skill is required
            stata = skill_test(['Stata', 'stata', 'STATA'])   #check if SAS skill is required
            vba = skill_test(['VBA'])   #check if SAS skill is required
            sql = skill_test(['SQL'])   #check if SQL skill is required
            power_bi = skill_test(['Power BI', 'PowerBI', 'powerBI', 'power BI', 'BI visualization'])       #check if Power BI skill is required

                                                            #set the new line of observation       
            obs = pd.DataFrame([[title, comp_name, location, t_work, t_contract, salary, excel, python, r, sas, stata, vba, sql, power_bi, sub_url]], columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA', 'SQL', 'POWER_BI', 'WEBSITE'])
            
            jobtab = pd.concat([jobtab, obs], axis=0)       #adding the new observation to the table

        try:
            main_url = browser.find_element(By.XPATH, '//head/link[@rel="next"]').get_attribute('href')
            browser.get(main_url)
        except NoSuchElementException:
            i = 1

    print(jobtab)

    try:
        deljobs = browser.find_element(By.CLASS_NAME, 'dupetext').text.split()[3]
        print(f'Note: {deljobs} jobs have been removed to avoid duplicated results')
    except: pass

    browser.close()

    jobtab.to_csv(file_path + '/jobs.csv', index=False, encoding='UTF-8', sep=';')       #save the database to csv file

    input_name.config(state='normal')
    input_place.config(state='normal')
    search_b.config(state='normal')


# Now we will build an interface for interacting with the program

def clear_name(x):
    input_name.delete(0, "end")

def clear_place(x):
    input_place.delete(0, "end")

# Define the properties of the window

root = Tk()
root.title("jobsearch")
root.geometry("720x350+400+230")    
root.resizable(0,0)

# creating the widgets

label1 = Label(root, text="Welcome to my jobsearch program!", font=('Times', 20))
label2 = Label(root, text="This program looks for the jobs which match your specific criteria on Indeed. \n You will be able to save the results in Excel.", font=('Times', 13))
copyright = Label(root, text=" ©by Frantz PDJ", font=('Times', 12, 'italic'))

label3 = Label(root, text="What job do you want to look for?")
input_name = Entry(root)
input_name.insert(0, "Name of the job")
label4 = Label(root, text="In what place (location) do you want the job?")
input_place = Entry(root)
input_place.insert(0, "City or location")
search_b = Button(root, text="Search", fg="blue", bg="lightgrey", command=search_jobs, font=('Helvetica', 11))
blank = Label(root, text="<------------------->")
blank2 = Label(root, text="")
blank3= Label(root, text="")
blank4= Label(root, text="")

# shoving the widgets on the screen

label1.pack(fill=BOTH, expand=TRUE)
label2.pack(fill=BOTH, expand=TRUE)
copyright.pack(fill=BOTH, expand=TRUE)
blank.pack(fill=BOTH, expand=TRUE)
blank2.pack(fill=BOTH, expand=TRUE)

label3.pack(fill=BOTH, expand=TRUE)
input_name.pack()
input_name.bind("<FocusIn>", clear_name)
blank3.pack(fill=BOTH, expand=TRUE)

label4.pack(fill=BOTH, expand=TRUE)
input_place.pack()
input_place.bind("<FocusIn>", clear_place)
blank4.pack(fill=BOTH, expand=TRUE)

search_b.pack()

# setting the main loop
root.mainloop()