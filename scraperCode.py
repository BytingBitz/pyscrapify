# Pull all reviews data from Indeed.com for specific organisations using provided arguments.
# Creation Date: 27/06/2021

from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
from math import ceil
import json
import csv
import re

# Function: grab_HTML
def grab_HTML(website, url, start, country=None, attempts=None):
    ''' Returns: Selected website page soup. '''
    if attempts is None: attempts = 1
    try:
        if website == "Indeed":
            req = lib.Request(url+'?start='+str(start)+'&fcountry='+country, 
                headers={'User-Agent': 'Mozilla/5.0'})
        else:
            req = lib.Request(url+'?page='+str(start),
                headers={'User-Agent': 'Mozilla/5.0'})
        webpage = lib.urlopen(req)
        return BeautifulSoup(webpage, 'html.parser')
    except:
        print(f"Page grab failed, retrying - {attempts}/15")
        attempts = attempts + 1
        if attempts > 15:
            print("Failed to grab HTML, crashed")
            exit(0)
        sleep(1)
        return grab_HTML(website, url, start, country, attempts)

# Function build_CSV
def build_CSV(filename, organisation, year, ratings, status, locations, positions, titles, reviews):
    ''' Returns: Built and named CSV file containing organisation review data. '''
    with open(filename + ".csv", 'w', newline = '', encoding = 'utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Organisation", "Year", "Rating", "Status", "Location", "Position", "Title", "Review"])
        print(len(organisation), len(year), len(ratings), len(status), len(locations), 
            len(positions), len(titles), len(reviews))
        for i in range(len(year)):
            writer.writerow([organisation[i], year[i], ratings[i], status[i], 
                locations[i], positions[i], titles[i], 
                repr(reviews[i])[1:-1]])

# Function: review_volume
def review_volume(soup, website, reviews_per_page):
    ''' Returns: Detected number reviews and number pages of reviews on website. '''
    try:
        if website == "Indeed":
            overview_data = soup.find('div', attrs={'data-testid': 'review-count'})
            try: number_reviews = int(overview_data.find('span').find('b').text.replace(',', ''))
            except: number_reviews = int(re.findall(r'\d+',overview_data.find('span').text)[0])
        else:
            overview_data = soup.find('div', attrs={'id': 'app'})
            number_reviews = int((overview_data.text.split("ReviewOverviewReviews"))[1].split("JobsTop")[0])
        number_pages = ceil((number_reviews - 1) / reviews_per_page)
    except:
        print(f"Failed to determine {website} review volume, crashed")
        exit(0)
    return number_reviews, number_pages
 
# Function: indeed_review_scrape
def indeed_scrape(organisation, url, output_name, country):
    ''' Returns: Review data for Indeed.com organisation as CSV with output name. '''
    print("Scraping Indeed reviews")
    global_soup = grab_HTML("Indeed", url, 0, country)
    reviews_per_page = 20
    ratings, positions, locations, titles, status, year, reviews = [],[],[],[],[],[],[]
    number_reviews, number_pages = review_volume(global_soup, "Indeed", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    for page in range(number_pages):
        sleep(1)
        print(f"Page {page + 1} of {number_pages}")
        # Configure to ignore first (duplicate) review after first page.
        if page == 0: soup, jump = global_soup, 0
        else: soup, jump = grab_HTML("Indeed", url, page * reviews_per_page, country), 1
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
    organisation = [organisation] * number_reviews
    build_CSV(output_name, organisation, year, ratings, status, locations, positions, titles, reviews)
    print("Finished")

# Function: seek_review_scrape
def seek_scrape(organisation, url, output_name):
    ''' Returns: Review data for Seek.com organisation as CSV with output name. '''
    print("Scraping Seek reviews")
    global_soup = grab_HTML("Seek", url, 1)
    reviews_per_page = 10
    ratings, positions, locations, titles, status, year, reviews = [],[],[],[],[],[],[]
    number_reviews, number_pages = review_volume(global_soup, "Seek", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    number_pages = 1
    for page in range(number_pages):
        sleep(1)
        print(f"Page {page + 1} of {number_pages}")
        soup = grab_HTML("Seek", url, page + 1) 
        json_content = soup.find('button', attrs={'script type': 'application/ld+json'})
        json_thing = json_content
        more_json = json_thing
        print(json.loads(more_json))
        # Extract location data.
        for location_data in soup.find_all('div', attrs={'id': 'work-location'}):
            locations.append(location_data.text)
        # Extract status data.
        for status_data in soup.find_all('div', attrs={'id': 'years-worked-with'}):
            if "current" in status_data.text: status.append("Current")
            if "former" in status_data.text: status.append("Former")
            else: status.append("Unknown")
        # Extract positions data and author text.

        # Extract status, location, and year data.
        
        # Extract rating data.
        
        # Extract title data.
        
        # Extract review data.
    print(status)
    organisation = [organisation] * number_reviews

seek_scrape("Kmart", "https://www.seek.com.au/companies/kmart-432302/reviews", "Seek_Kmart")


# Scrape reviews of a single organisation.
#indeed_scrape("Target", "https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")

# Function: multi_review_scrape
def multi_scrape(data=None):
    ''' Returns: Review data for multiple Indeed.com organisation as CSV files. '''
    # Load data from file if none is supplied.
    if not data:
        with open("organisations.json") as content:
            data = json.load(content)
    number_scrapes = len(data["configs"])
    print(f"Found {number_scrapes} organisation reviews to scrape ")
    for i in range(number_scrapes):
        config = data["configs"][i]
        url = config.get("url")
        name = config.get("name")
        country = config.get("country")
        print(f"Organisation {i + 1} of {number_scrapes}")
        indeed_scrape(url, name, country)
    print("All organisations finished")

# Scrape reviews of multiple organisations.    
#multi_review_scrape()
