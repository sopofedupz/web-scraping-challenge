
# coding: utf-8

import warnings
warnings.filterwarnings('ignore')

# Dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import time
import requests
import json

def init_browser():
    """Set executable path and initialize Chrome browser"""
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless = True)

def scrape():
    """Scrapes various websites for information and returns data in a dictionary"""

    browser = init_browser()
    mars_data = {}

    # Visit the NASA Mars news website and scrape latest headline
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    time.sleep(1)

    # Create a Beautiful Soup object
    html = browser.html
    news_soup = bs(html, "html.parser")

    # Get the list of articles
    news_list = news_soup.find('ul', class_='item_list')

    # Get the title of the latest news
    latest_article = news_list.find("div", class_ = "content_title").text

    # Get the paragraph text of the latest news article
    article_teaser = news_list.find("div", class_ = "article_teaser_body").text

    # Add scraped data to dict
    mars_data['headline'] = latest_article
    mars_data['teaser'] = article_teaser
 
    # Visit the JPL website and scrape the featured image
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)

    time.sleep(1)

    # Using splinter to click on the full image button of the featured image
    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(1)

    # Using splinter to click on the full image button of the featured image
    browser.click_link_by_partial_text('more info')

    time.sleep(1)

    # Scrape page into Soup
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, "html.parser")

    # Get the featured image link
    jpl_featured_image = jpl_soup.find("img", class_="main_image")['src']

    # Create the full link
    featured_image_url = "https://www.jpl.nasa.gov" + jpl_featured_image
    
    # Add scraped link to dict
    mars_data['featured_image_url'] = featured_image_url

    # Visit the Mars Weather twitter account and scrape the latest tweet
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"

    # Scraping the latest Mars Weather tweet using request

    response=requests.get(mars_weather_url)

    # Scraping the response content into Soup
    mars_weather_soup = bs(response.content,'lxml')
    all_tweets = mars_weather_soup.find_all('div',{'class':'tweet'})

    # Creating an empty tweet list
    tweet_list = []

    # Looping through all the tweets and appending only those tweeted by Mars Weather user
    if all_tweets:
    
        for tweet in all_tweets:
            content = tweet.find('div',{'class':'content'})
            header = content.find('div',{'class':'stream-item-header'})
            user = header.find('a',{'class':'account-group js-account-group js-action-profile js-user-profile-link js-nav'}).text.replace("\n"," ").strip()
            message = content.find('div',{'class':'js-tweet-text-container'}).text.replace("\n"," ").strip()
            
            if user == "Mars Weather\u200f\xa0@MarsWxReport":
                tweet_list.append(message)
            
        else:
            print("List is empty/account name not found.")
        
    # Selecting the latest tweet
    mars_weather = tweet_list[1]

    # Add scraped data to dict
    mars_data['mars_weather'] = mars_weather

    # Visit Mars Facts webpage and scrape the facts table
    mars_facts_url = "https://space-facts.com/mars/"

    # Use pandas to parse the url
    tables = pd.read_html(mars_facts_url)

    # Selecting the table and putting into a dataframe
    try:
        mars_facts_df = tables[0]
        mars_facts_df.columns = ["Planetary Attributes", "Values"]
    except:
        mars_facts_df = tables[1]
        mars_facts_df.columns = ["Planetary Attributes", "Values"]

    # Convert data in table to html
    mars_facts_html = mars_facts_df.to_html(index=False, header=False)

    # adding scraped table to dict
    mars_data['mars_facts_table'] = mars_facts_html

    # Visit USGS website and scrape the hemisphere images
    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(usgs_url)

    time.sleep(1)

    # Scrape page into Soup
    usgs_html = browser.html
    usgs_soup = bs(usgs_html, "html.parser")

    item = usgs_soup.find_all("div", class_ = "item")

    # Create a list of the titles
    names = usgs_soup.find_all('h3')

    # Create an empty list for the image links
    hemisphere_image_urls = []

    # Loop through all the items on the page to get the links and names
    for i in range(0,len(item)):
        
        hemisphere_dict = {}
        
        # get the list of titles with the element stripped off
        title = names[i].text.strip("Enhanced").strip(" ")
        #titles.append(title)
        hemisphere_dict["title"] = title
        
        # clicking on each item to get the image link/url
        browser.visit(usgs_url)
        time.sleep(1)
        browser.click_link_by_partial_text(title)
        time.sleep(1)
        hemisphere_html = browser.html
        time.sleep(1)
        hemisphere_soup = bs(hemisphere_html, "html.parser")
        hemisphere_link = hemisphere_soup.find("div", class_ = "downloads").find('ul').find('li').find('a')['href']
        hemisphere_dict["img_url"] = hemisphere_link
        
        hemisphere_image_urls.append(hemisphere_dict)

    # add scraped data in dict
    mars_data['hemisphere_img'] = hemisphere_image_urls

    browser.quit()

    return mars_data