import numpy as np 
import scipy as sp
import os
import re
import pickle
import time
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from matplotlib import pyplot as plt

def tag_visible(element):
    """
    Function taken from stack overflow ("https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text")
    that gives all the visible text of a given list of tag text
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def relations(relate_soup):
    """
    return a list of dictionaries of the parents, children, or collaborators
    """
    lis = []
    for r in relate_soup.find_all('tr'):
        relation = {}
        types = r.find_all('td')
        
        if len(types)==4:
            relation['name'] = types[0].text.strip()
            relation['type'] = types[1].text.strip()
            relation['year'] = types[2].text.strip()
            relation['location'] = types[3].text.strip()
            lis.append(relation)
    return lis




def scrape(base_url = "https://academictree.org/physics/tree.php?pid=689916&pnodecount=6&cnodecount=2&fontsize=1",lag_time=10):
    """
    Given page with 6 generations, scrape all the people's names, universities (if a university is listed), and links to each person's individual tree
    """

    # Set up browser
    browser = webdriver.Chrome()

    try:
        browser.get(base_url)

        # get all the relevant tags
        tags = browser.find_elements_by_class_name("centerNode")
        names = [tag.text for tag in tags]                       # get the text from each of the tags
        links = [tag.get_attribute('href') for tag in tags]      # get the links from each of the tags
    finally:
        browser.close()
    return names,links

def scrape_bio_pages(All, lag_time=10):
    """
    Go through scraped links and scrape each individual's bio page.
    Parameters:
        All: dictionary of all scraped names paired with their urls
    Returns:
        people: dictionary of each person, keyed by names
    """

    # dictionary to store each individual's information from their bio page
    people = {}

    # iterate through all the links
    for x in All.keys():
        url = All[x]
        person = {}
        browser = webdriver.Chrome()
        try:
            browser.get(url)
            # navigate to the individual's bio page, if the given url isn't already for the bio page
            if 'peopleinfo' not in url:
                bio_page = browser.find_element_by_id("centerNodeName")
                bio_page.click()

            # turn the bio page into soup
            soup = BeautifulSoup(browser.page_source,'html.parser')

            # get all the information from the personal info section
            personal_info = soup.find(class_='personinfo')
            info_texts = personal_info.find_all(text=True)
            person['personal_info'] = u" ".join(t.strip() for t in filter(tag_visible,info_texts))

            # get the left hand side of the bio page, and split up into parents, children, and collaborators
            leftside = soup.find(class_="leftcol")
            relate = leftside.find_all(class_="connection_list")
            parents, children, collabs = relate[0],relate[1],relate[2]

            # get all the information about the parents
            person['parents'] = relations(parents)

            # get all the information about the children
            person['children'] = relations(children)

            # get all the information about collaborators
            person['collaborators'] = relations(collabs)

            # get the number of publications (may scrape the seperate page of publications in a later iteration of this scraper)
            """pub_page = browser.find_element_by_partial_link_text('publications')
            print(pub_page)
            pub_page.click()
            print(browser.page_source)

            pub_soup = BeautifulSoup(browser.page_source,'html.parser')"""


            people[x]=person

        finally:
            browser.close()

    return people

def save_data(Names1=[],filename="data.pickle",hyperlinks=["https://academictree.org/physics/tree.php?pid=522565&fontsize=1&pnodecount=6&cnodecount=2","https://academictree.org/physics/tree.php?pid=645114&pnodecount=6&cnodecount=2&fontsize=1","https://academictree.org/physics/tree.php?pid=132066&pnodecount=5&cnodecount=2&fontsize=1","https://academictree.org/physics/tree.php?pid=522596&fontsize=1&pnodecount=4&cnodecount=2","https://academictree.org/physics/tree.php?pid=128164&fontsize=1&pnodecount=6&cnodecount=2","https://academictree.org/physics/tree.php?pid=754877&fontsize=1&pnodecount=6&cnodecount=2","https://academictree.org/physics/tree.php?pid=162494&fontsize=1&pnodecount=6&cnodecount=2","https://academictree.org/physics/tree.php?pid=685925&fontsize=1&pnodecount=4&cnodecount=2","https://academictree.org/physics/tree.php?pid=59203&fontsize=1&pnodecount=4&cnodecount=2","https://academictree.org/physics/tree.php?pid=139206&fontsize=1&pnodecount=4&cnodecount=2"]):
    """
    Scrape the physics acadeimc tree and store the resulting dictionary
    """
    # scrape all the names and personal tree urls from the given hyperlinks
    Names,Links=[],[]
    for link in hyperlinks:
        names,links = scrape(base_url=link)
        Names.extend(names)
        Links.extend(links)

    # get rid of duplicates
    All = {}
    for i in range(len(Names)):
        if Names[i] not in All.keys() and Names[i] not in Names1:
            All[Names[i]] = Links[i]

    # scrape the bio pages for each person
    people = scrape_bio_pages(All)

    # pickle the dictionary
    with open(filename,'wb') as handle:
        pickle.dump(people,handle,protocol=pickle.HIGHEST_PROTOCOL)

def load_data(filename='data.pickle'):
    """
    Load in the pickled dictionary
    """
    with open(filename,'rb') as handle:
        people = pickle.load(handle)

    return people