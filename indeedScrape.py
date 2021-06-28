# Pull all reviews data from Indeed.com for specific organisations using provided arguments.
# Creation Date: 27/06/2021

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
from math import ceil
from json import load
import csv
import re

# Desired Data:
ratings, positions, locations, titles, status, year, reviews = [],[],[],[],[],[],[]
load_dotenv()

# Function: grabHTML
def grabHTML(url, start, country):
    ''' Returns: Selected Indeed.com page soup. '''
    try:
        req = lib.Request(url+'?start='+str(start)+'&fcountry='+country, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = lib.urlopen(req)
        return BeautifulSoup(webpage, 'html.parser')
    except:
        print("Page grab failed, retrying")
        sleep(1)
        return grabHTML(url, start, country)

# Function buildCSV
def buildCSV(fileName, year, ratings, status, locations, positions, titles, reviews):
    ''' Returns: Built and named CSV file containing organisation review data. '''
    with open(fileName + ".csv", 'w', newline = '', encoding = 'utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Year", "Rating", "Status", "Location", "Position", "Title", "Review"])
        print(len(year), len(ratings), len(status), len(locations), 
            len(positions), len(titles), len(reviews))
        for i in range(len(year)):
            writer.writerow([year[i], ratings[i], status[i], 
                locations[i], positions[i], titles[i], repr(reviews[i])[1:-1]])

# Function: reviewScrape
def reviewScrape(url, outputName, country):
    ''' Returns: Review data for Indeed.com organisation as CSV with output name. '''
    globalSoup = grabHTML(url, 0, country)
    reviewsPerPage = 20
    overviewData = globalSoup.find('div', attrs={'data-testid': 'review-count'})
    try: numberReviews = int(overviewData.find('span').find('b').text.replace(',', ''))
    except: numberReviews = int(re.findall(r'\d+',overviewData.find('span').text)[0])
    numberPages = ceil((numberReviews - 1) / reviewsPerPage)
    print(f"Found {numberReviews} reviews")
    for page in range(numberPages):
        sleep(1)
        print(f"Page {page + 1} of {numberPages}")
        if page == 0: soup, jump = globalSoup, 0
        else: soup, jump = grabHTML(url, page * reviewsPerPage, country), 1
        # Extract positions data and author text.
        authorText = []
        for authorData in soup.find_all('span', attrs={'itemprop': 'author'})[jump:]:
            positions.append(authorData.find('meta').attrs['content'])
            authorText.append(authorData.text)
        # Extract status, location, and year data.
        for authorEntry in authorText:
            splitData = authorEntry.rsplit(' - ', 2)
            if "(Current Employee)" in splitData[0]: status.append("Current")
            else: status.append("Former")
            locations.append(splitData[1])
            year.append(splitData[2][-4:])
        # Extract rating data.
        for ratingData in soup.find_all('div', attrs={'itemprop': 'reviewRating'})[jump:]:
            ratings.append(ratingData.find('meta').attrs['content'])
        # Extract title data.
        for titleData in soup.find_all('h2', attrs={'data-testid': 'title'})[jump:]:
            titles.append(titleData.text)
        # Extract review data.
        for reviewData in soup.find_all('span', attrs={'itemprop': 'reviewBody'})[jump:]:
            reviews.append(reviewData.text)
    buildCSV(outputName, year, ratings, status, locations, positions, titles, reviews)
    print("Finished")

# Scrape reviews of a single organisation.
reviewScrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")

# Function: multiReviewScrape
def multiReviewScrape():
    ''' Returns: Review data for multiple Indeed.com organisation as CSV files. '''
    with open("organisations.json") as content:
         data = load(content)
    numberScrapes = len(data["urls"])
    print(f"Found {numberScrapes} organisation reviews to scrape ")
    for org in range(numberScrapes):
        print(f"Organisation {org + 1} of {numberScrapes}")
        reviewScrape(data["urls"][org], data["names"][org], data["countries"][org])
    print("All organisations finished")

# Scrape reviews of multiple organisations.    
#multiReviewScrape()
