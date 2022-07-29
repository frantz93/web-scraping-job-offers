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
    excel_sk.config(state='disabled')
    python_sk.config(state='disabled')
    r_sk.config(state='disabled')
    sas_sk.config(state='disabled')
    stata_sk.config(state='disabled')
    vba_sk.config(state='disabled')
    sql_sk.config(state='disabled')
    powbi_sk.config(state='disabled')
    search_mode.config(state='disabled')
    search_b.config(state='disabled')

    file_path = filedialog.askdirectory()

    search_name = input_name.get()   #save the job title the user wants to search for
    search_place = input_place.get()        #save the job location the user wants to search for
    t_excel = excel_var.get()      #next, save the skills choices
    t_python = python_var.get() 
    t_r = r_var.get() 
    t_sas = sas_var.get() 
    t_stata = stata_var.get() 
    t_vba = vba_var.get() 
    t_sql = sql_var.get() 
    t_powbi = powbi_var.get() 

    t_sm = sm.get()       #also, store the prefered search_mode

    #we build the list of selected and not selected skills
    sel_skills = []
    not_skills = []
    skills_result = [t_excel, t_python, t_r, t_sas, t_stata, t_vba, t_sql, t_powbi]
    print(skills_result)
    skills_names = [tuple(['Excel', 'excel', 'EXCEL', 'MSExcel', 'MSexcel']), tuple(['Python', 'python', 'PYTHON']), tuple(['R,', 'R.', 'R)']), tuple(['SAS']), tuple(['Stata', 'stata', 'STATA']), tuple(['VBA']), tuple(['SQL']), tuple(['Power BI', 'PowerBI', 'powerBI', 'power BI', 'BI visualization'])]
    #skills_names = [['Excel', 'excel', 'EXCEL', 'MSExcel', 'MSexcel'], ['Python', 'python', 'PYTHON'], ['R,', 'R.', 'R'], ['SAS'], ['Stata', 'stata', 'STATA'], ['VBA'], ['SQL'], ['Power BI', 'PowerBI', 'powerBI', 'power BI', 'BI visualization']]

    for skn in skills_names:
        if skills_result[skills_names.index(skn)] == True:
            sel_skills.append(skn)
    not_skills = list(set(skills_names) - set(sel_skills))
    print(f'selected skills: {sel_skills}')
    print(f'unselected skills: {not_skills}')
    

    #skills_names = ['excel', 'python', 'r', 'sas', 'stata', 'vba', 'sql', 'power_bi']
    #skills_result = [True, False, True, False, False, False, True, False]
    #skills_names = ['excel', 'vba', 'python', 'stata']
    #for each in skills_names:
    #    if skills_result[skills_names.index(each)] == True:
    #        skills_list.append(each)
    #print(skills_list)


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
        t = nb * 4      #total time in seconds (about 3 seconds per page)
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
            for val in x:        
                result_list.append(val in string)  # append True/False for each element in substring
            r = any(result_list) #call any() with boolean results list
            if r == True:
                result = 'yes'
            else:
                result = 'no'
        except: pass
        return result

    def test_state(x):
        states = ''
        for ste in x[:-1]:
            states = states + f'contains(text(), "{ste}") or '
        states = states + f'contains(text(), "{x[-1]}")'
        return states

    can_states = ["AB", "BC", "PE", "MB", "NB", "NS", "NU", "ON", "QC", "SK", "NL", "NT", "YT"]


    #next lines allow to navigates through all the pages containing job announcement and store relevant data in a dataframe

    jobtab = pd.DataFrame(columns=['TITLE', 'COMPANY', 'LOCATION', 'T_WORK', 'T_CONTRACT', 'SALARY', 'EXCEL', 'PYTHON', 'R', 'SAS', 'STATA', 'VBA', 'SQL', 'POWER_BI', 'WEBSITE'])

    #collecting the jobs' access links
    links = []
    i = 0
    while i == 0:
        for job in browser.find_elements(By.XPATH, '//a[@class="jcs-JobTitle css-jspxzf eu4oa1w0"]'):
            links.append(job.get_attribute('href'))
        try:
            main_url = browser.find_element(By.XPATH, '//head/link[@rel="next"]').get_attribute('href')
            browser.get(main_url)
            time.sleep(2)
        except NoSuchElementException:
            i = 1

    print(f'We found {len(links)} jobs that may match your request. We will explore more deeply. Estimated time is {delay(len(links))}.')


    #downloading data on the jobs

    id = 0
    for each in links:
        browser.get(each)
        time.sleep(2)

        #Commands to report data from web pages to database

        print(f'test of job number {links.index(each)+1}')
        
        #first we check if the job matches the user reported skills
        j = 0
        k = 0
        if t_sm =='No':
            for sks in sel_skills:
                res = skill_test(sks)
                print(f'Selected skill #{sel_skills.index(sks)+1} is found: {res}')
                if res == 'yes':
                    j = 1
                    k = 0
                    break
                #break
        elif t_sm == 'Yes':
            for sks in sel_skills:
                res1 = skill_test(sks)
                print(f'Selected skill #{sel_skills.index(sks)+1} is found: {res1}')
                if res1 == 'yes':
                    j = 1
                    for nsks in not_skills:
                        res2 = skill_test(nsks)
                        print(f'Ignored skill #{not_skills.index(nsks)+1} is found: {res2}')
                        if res2 == 'yes':
                            k = 1
                            break
                break


        if j == 1 and k == 0:
        
            title = ''
            comp_name = ''
            location = ''
            t_work = ''
            t_contract =''
            salary = ''
            website = ''

            id = id + 1

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
                t_contract = browser.find_element(By.XPATH, '//span[contains(@class,"jobsearch-JobMetadataHeader")]').text.replace('-','')    #type of contract (full time/part time, casual/permanent)
            except: pass
            
            try:
                salary = browser.find_element(By.XPATH, '//span[@class="icl-u-xs-mr--xs attribute_snippet"]').text.replace('-',' to ')      #salary
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

    print(f'Result Summary: {id} jobs were found that meet your characteristics')

    print(jobtab)

    browser.close()
    
    #temporary code to replace some characters
    l1 = ['é', 'à', 'î', 'ô', 'è', 'ù', 'ò', 'â', 'ê', 'í', 'á', 'ñ', 'ì', 'ö', 'ï', 'ë', 'ç', 'ä', 'ü']
    l2 = ['e', 'a', 'i', 'o', 'e', 'u', 'o', 'a', 'e', 'i', 'a', 'n', 'i', 'o', 'i', 'e', 'c', 'a', 'u']
    jobtab = jobtab.replace(l1,l2, regex=True)

    #save the dataframe to excel file
    jobtab.to_csv(file_path + '/jobs.csv', index=False, encoding='UTF-8', sep=';')       #save the database to csv file

    input_name.config(state='normal')
    input_place.config(state='normal')
    excel_sk.config(state='normal')
    python_sk.config(state='normal')
    r_sk.config(state='normal')
    sas_sk.config(state='normal')
    stata_sk.config(state='normal')
    vba_sk.config(state='normal')
    sql_sk.config(state='normal')
    powbi_sk.config(state='normal')
    search_mode.config(state='normal')
    search_b.config(state='normal')

# Now we will build an interface for interacting with the program

def clear_name(x):
    input_name.delete(0, "end")

def clear_place(x):
    input_place.delete(0, "end")

# Define the properties of the window

root = Tk()
root.title("jobsearch")
root.geometry("720x640+400+90")    
#root.resizable(0,0)

# creating the widgets

welcome = Label(root, text="Welcome to my jobsearch program!", font=('Times', 20))
descr = Label(root, text="This program looks for the jobs which match your specific criteria on Indeed. \n You will be able to save the results in Excel.", font=('Times', 13))
copyright = Label(root, text=" ©by Frantz PDJ", font=('Times', 12, 'italic'))

q1 = Label(root, text="What job do you want to look for?", font=('Times', 12))
input_name = Entry(root)
input_name.insert(0, "Name of the job")

q2 = Label(root, text="In what place (location) do you want the job?", font=('Times', 12))
input_place = Entry(root)
input_place.insert(0, "City or location")

q3 = Label(root, text="What are your computer skills?", font=('Times', 12))
excel_var = BooleanVar()
python_var = BooleanVar()
r_var = BooleanVar()
sas_var = BooleanVar()
stata_var = BooleanVar()
vba_var = BooleanVar()
sql_var = BooleanVar()
powbi_var = BooleanVar()

excel_sk = Checkbutton(root, text='EXCEL', variable =excel_var, onvalue=True, offvalue=False)
python_sk = Checkbutton(root, text='PYTHON', variable =python_var, onvalue=True, offvalue=False)
r_sk = Checkbutton(root, text='R', variable =r_var, onvalue=True, offvalue=False)
sas_sk = Checkbutton(root, text='SAS', variable =sas_var, onvalue=True, offvalue=False)
stata_sk = Checkbutton(root, text='STATA', variable =stata_var, onvalue=True, offvalue=False)
vba_sk = Checkbutton(root, text='VBA', variable =vba_var, onvalue=True, offvalue=False)
sql_sk = Checkbutton(root, text='SQL', variable =sql_var, onvalue=True, offvalue=False)
powbi_sk = Checkbutton(root, text='POWER_BI', variable =powbi_var, onvalue=True, offvalue=False)

q4 = Label(root, text="Restrict my reseach to the selected skills above:", font=('Times', 12))
OptionList = ["","Yes", "No"] 
sm = StringVar(root)
sm.set(OptionList[0])
search_mode = OptionMenu(root, sm, *OptionList)
search_mode.config(width=3, font=('Calibri', 10))

search_b = Button(root, text="Search", fg="blue", bg="lightgrey", command=search_jobs, font=('Helvetica', 11))
blank = Label(root, text="<------------------->")
blank2 = Label(root, text="")
blank3= Label(root, text="")
blank4= Label(root, text="")
blank5= Label(root, text="")
blank6= Label(root, text="")

# shoving the widgets on the screen

welcome.pack(fill=BOTH, expand=TRUE)
descr.pack(fill=BOTH, expand=TRUE)
copyright.pack(fill=BOTH, expand=TRUE)
blank.pack(fill=BOTH, expand=TRUE)
blank2.pack(fill=BOTH, expand=TRUE)

q1.pack(fill=BOTH, expand=TRUE)
input_name.pack()
input_name.bind("<FocusIn>", clear_name)
blank3.pack(fill=BOTH, expand=TRUE)

q2.pack(fill=BOTH, expand=TRUE)
input_place.pack()
input_place.bind("<FocusIn>", clear_place)
blank4.pack(fill=BOTH, expand=TRUE)

q3.pack(fill=BOTH, expand=TRUE)
excel_sk.pack(fill=BOTH, expand=TRUE)
python_sk.pack(fill=BOTH, expand=TRUE)
r_sk.pack(fill=BOTH, expand=TRUE)
sas_sk.pack(fill=BOTH, expand=TRUE)
stata_sk.pack(fill=BOTH, expand=TRUE)
vba_sk.pack(fill=BOTH, expand=TRUE)
sql_sk.pack(fill=BOTH, expand=TRUE)
powbi_sk.pack(fill=BOTH, expand=TRUE)
blank5.pack(fill=BOTH, expand=TRUE)

q4.pack(fill=BOTH, expand=TRUE)
search_mode.pack()
blank6.pack(fill=BOTH, expand=TRUE)

search_b.pack()

# setting the main loop
root.mainloop()