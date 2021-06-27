# Pull all reviews data from Indeed.com for specific organisation using provided URL, produce CSV.
# Creation Date: 

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.request as lib
from random import randint
from time import sleep
from math import ceil
from os import getenv

# Desired Data:
ratings, positions, locations, titles, status, year, reviews = [],[],[],[],[],[],[]
load_dotenv()

# Function: grabHTML
def grabHTML(url, start):
    ''' Returns: Selected Indeed.com page soup. '''
    req = lib.Request(url + '?fcountry=ALL&start=' + str(start), headers={'User-Agent': 'Mozilla/5.0'})
    webpage = lib.urlopen(req)
    return BeautifulSoup(webpage, 'html.parser')

# Function: reviewScrape
def reviewScrape(url, outputName):
    ''' Returns: Review data for Indeed.com organisation as CSV with output name. '''

    # Grab first page.
    globalSoup = grabHTML(url, 0)

    # Extract number pages.
    reviewsPerPage = 20
    overviewData = globalSoup.find('div', attrs={'itemprop': 'aggregateRating'})
    numberReviews = int(overviewData.find('meta').attrs['content'])
    numberPages = ceil(numberReviews - 1 / reviewsPerPage)
    numberPages = 1 # Temp to limit requests

    # Iterate through each page of reviews.
    for page in range(numberPages):

        # Sleep randomly first.
        sleep(randint(0, 3))
        # After first page, ignore featured review and update HTML.
        if page == 0: soup, jump = globalSoup, 0
        else: soup, jump = grabHTML(url, page * reviewsPerPage), 1

        # Extract positions data and author text.
        authorText = []
        for authorData in soup.find_all('span', attrs={'itemprop': 'author'})[jump:]:
            positions.append(authorData.find('meta').attrs['content'])
            authorText.append(authorData.text)
        # Extract status, location, year data.
        for authorEntry in authorText:
            splitData = authorEntry.split(' - ', 2)
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

reviewScrape(getenv('URL'), getenv('NAME'))
