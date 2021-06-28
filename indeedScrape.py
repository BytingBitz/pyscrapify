# Pull all reviews data from Indeed.com for specific organisations using provided arguments.
# Creation Date: 27/06/2021

from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
from math import ceil
from json import load
import csv
import re

# Function: grab_HTML
def grab_HTML(url, start, country):
    ''' Returns: Selected Indeed.com page soup. '''
    try:
        req = lib.Request(url+'?start='+str(start)+'&fcountry='+country, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = lib.urlopen(req)
        return BeautifulSoup(webpage, 'html.parser')
    except:
        print("Page grab failed, retrying")
        sleep(1)
        return grab_HTML(url, start, country)

# Function build_CSV
def build_CSV(filename, year, ratings, status, locations, positions, titles, reviews):
    ''' Returns: Built and named CSV file containing organisation review data. '''
    with open(filename + ".csv", 'w', newline = '', encoding = 'utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Year", "Rating", "Status", "Location", "Position", "Title", "Review"])
        print(len(year), len(ratings), len(status), len(locations), 
            len(positions), len(titles), len(reviews))
        for i in range(len(year)):
            writer.writerow([year[i], ratings[i], status[i], 
                locations[i], positions[i], titles[i], 
                repr(reviews[i])[1:-1]])

# Function: review_scrape
def review_scrape(url, output_name, country):
    ''' Returns: Review data for Indeed.com organisation as CSV with output name. '''
    global_soup = grab_HTML(url, 0, country)
    reviews_per_page = 20
    ratings, positions, locations, titles, status, year, reviews = [],[],[],[],[],[],[]
    overview_data = global_soup.find('div', attrs={'data-testid': 'review-count'})
    try: number_reviews = int(overview_data.find('span').find('b').text.replace(',', ''))
    except: number_reviews = int(re.findall(r'\d+',overview_data.find('span').text)[0])
    number_pages = ceil((number_reviews - 1) / reviews_per_page)
    print(f"Found {number_reviews} reviews")
    for page in range(number_pages):
        sleep(1)
        print(f"Page {page + 1} of {number_pages}")
        if page == 0: soup, jump = global_soup, 0
        else: soup, jump = grab_HTML(url, page * reviews_per_page, country), 1
        # Extract positions data and author text.
        author_text = []
        for author_data in soup.find_all('span', attrs={'itemprop': 'author'})[jump:]:
            positions.append(author_data.find('meta').attrs['content'])
            author_text.append(author_data.text)
        # Extract status, location, and year data.
        for author_entry in author_text:
            split_data = author_entry.rsplit(' - ', 2)
            if "(Current Employee)" in split_data[0]: status.append("Current")
            else: status.append("Former")
            locations.append(split_data[1])
            year.append(split_data[2][-4:])
        # Extract rating data.
        for rating_data in soup.find_all('div', attrs={'itemprop': 'reviewRating'})[jump:]:
            ratings.append(rating_data.find('meta').attrs['content'])
        # Extract title data.
        for title_data in soup.find_all('h2', attrs={'data-testid': 'title'})[jump:]:
            titles.append(title_data.text)
        # Extract review data.
        for review_data in soup.find_all('span', attrs={'itemprop': 'reviewBody'})[jump:]:
            reviews.append(review_data.text)
    build_CSV(output_name, year, ratings, status, locations, positions, titles, reviews)
    print("Finished")

# Scrape reviews of a single organisation.
#review_scrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")

# Function: multi_review_scrape
def multi_review_scrape(data=None):
    ''' Returns: Review data for multiple Indeed.com organisation as CSV files. '''
    # Load data from file if none is supplied.
    if not data:
        with open("organisations.json") as content:
            data = load(content)
    number_scrapes = len(data["configs"])
    print(f"Found {number_scrapes} organisation reviews to scrape ")
    for i in range(number_scrapes):
        config = data["configs"][i]
        url = config.get("url")
        name = config.get("name")
        country = config.get("country")
        print(f"Organisation {i + 1} of {number_scrapes}")
        review_scrape(url, name, country)
    print("All organisations finished")

# Scrape reviews of multiple organisations.    
multi_review_scrape(None)
