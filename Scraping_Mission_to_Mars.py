# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd 
import datetime as dt 

# Path to chromedriver
#!which chromedriver

# Set the executable path
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}

def scrape_all():
    #  initialize the chrome browser in splinter
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # end automated browsing session and return data
    browser.quit()
    return data

#Function:
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # set up HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    slide_elem = news_soup.select_one('ul.item_list li.slide')

    # add try/except for error handling 
    try:
        # Start scraping
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        
    except AttributeError:

        return None, None

    return news_title, news_p


### Featured Image

# Function: featured image
def featured_image(browser):

    # visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # add try and except block for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    

    return img_url

### Mars Facts
# function for table facts
def mars_facts():
    try:
        # Scrape facts table and create as pandas dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description','value']
    df.set_index('description', inplace=True)

    # convert pandas DF to html ready code, add bootstrap
    return df.to_html()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())