from bs4 import BeautifulSoup
import urllib.request as lib
from pathlib import Path
from time import sleep
from math import ceil
import json
import csv
import re

# Function: grab_HTML
def grab_HTML(website, seek_url, start, country=None, attempts=None):
    ''' Returns: Selected website page soup. '''
    if attempts is None:
        attempts = 1
    try:
        # Build url based on website, return soup.
        if website == "Indeed":
            req = lib.Request(seek_url+'?start='+str(start)+'&fcountry='+country,
                              headers={'User-Agent': 'Mozilla/5.0'})
        else:
            req = lib.Request(seek_url+'?page='+str(start),
                              headers={'User-Agent': 'Mozilla/5.0'})
        webpage = lib.urlopen(req)
        return BeautifulSoup(webpage, 'html.parser')
    except:
        # If page grab fails, retry up to 15 times.
        print(f"Page grab failed, retrying - {attempts}/15")
        attempts = attempts + 1
        if attempts > 15:
            print("Failed to grab HTML, crashed")
            exit(0)
        sleep(1)
        return grab_HTML(website, seek_url, start, country, attempts)

# Function append_CSV
def append_CSV(filename, organisation, website, year, ratings,
               status, locations, positions, titles, reviews):
    ''' Returns: Built and named CSV file containing organisation review data. '''
    root = Path('/' + filename + '.csv')
    # Check if file is new and requires headings.
    headings = False
    if root.exists():
        headings = True
    with open(filename + ".csv", 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if headings == True:
            writer.writerow(["Organisation", "Website", "Year", "Rating",
                             "Status", "Location", "Position", "Title", "Review"])
        # If these values don't match, something went wrong.
        print(len(organisation), len(website), len(year), len(ratings), len(status),
              len(locations), len(positions), len(titles), len(reviews))
        # Write generated data to CSV files by row.
        for i in range(len(year)):
            writer.writerow([organisation[i], website[i], year[i], ratings[i], status[i],
                             locations[i], positions[i], repr(titles[i])[1:-1], repr(reviews[i])[1:-1]])

# Function: review_volume
def review_volume(soup, website, reviews_per_page):
    ''' Returns: Detected number reviews and number pages of reviews on website. '''
    try:
        if website == "Indeed":
            overview_data = soup.find(
                'div', attrs={'data-testid': 'review-count'})
            # Pull Indeed review count, second method may be necessary.
            try:
                number_reviews = int(overview_data.find(
                    'span').find('b').text.replace(',', ''))
            except:
                number_reviews = int(re.findall(
                    r'\d+', overview_data.find('span').text)[0])
        elif website == "Seek":
            # Pull Seek review count.
            overview_data = soup.find('div', attrs={'id': 'app'})
            number_reviews = int((overview_data.text.split(
                "ReviewOverviewReviews"))[1].split("JobsTop")[0])
        # Calculate number pages.
        number_pages = ceil((number_reviews - 1) / reviews_per_page)
        return number_reviews, number_pages
    except:
        print(f"Failed to determine {website} review volume, crashed")
        exit(0)

# Function: indeed_review_scrape
def indeed_scrape(organisation, indeed_url, output_name, indeed_country):
    ''' Returns: Review data for Indeed.com organisation as CSV with output name. '''
    print("Scraping Indeed reviews")
    global_soup = grab_HTML("Indeed", indeed_url, 0, indeed_country)
    reviews_per_page = 20
    ratings, positions, locations, titles, status, year, reviews = [], [], [], [], [], [], []
    number_reviews, number_pages = review_volume(
        global_soup, "Indeed", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    for page in range(number_pages):
        sleep(1)
        print(f"Page {page + 1} of {number_pages}")
        # Configure to ignore first (duplicate) review after first page.
        if page == 0:
            soup, jump = global_soup, 0
        else:
            soup, jump = grab_HTML("Indeed", indeed_url,
                                   page * reviews_per_page, indeed_country), 1
        # Extract positions data and author text.
        author_text = []
        for author_data in soup.find_all('span', attrs={'itemprop': 'author'})[jump:]:
            positions.append(author_data.find('meta').attrs['content'])
            author_text.append(author_data.text)
        # Extract status, location, and year data.
        for author_entry in author_text:
            split_data = author_entry.rsplit(' - ', 2)
            if "(Current Employee)" in split_data[0]:
                status.append("Current")
            else:
                status.append("Former")
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
    # Prepare and build CSV file.
    organisations = [organisation] * number_reviews
    website = ["Indeed"] * number_reviews
    append_CSV(output_name, organisations, website, year, ratings,
               status, locations, positions, titles, reviews)
    print("Finished")

# Function: seek_review_scrape
def seek_scrape(organisation, seek_url, output_name):
    ''' Returns: Review data for Seek.com organisation as CSV with output name. '''
    print("Scraping Seek reviews")
    global_soup = grab_HTML("Seek", seek_url, 1)
    reviews_per_page = 10
    ratings, positions, locations, titles, status, year, reviews = [], [], [], [], [], [], []
    number_reviews, number_pages = review_volume(
        global_soup, "Seek", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    # Find parent_class hash constant for location and status HTML data.
    parent_class = None
    for page in range(number_pages):
        try:
            soup = grab_HTML("Seek", seek_url, page + 1)
            optional_data = soup.find('div', attrs={'id': 'work-location'})
            parent_class = ((str(optional_data.find_parent('div')).split(
                '<div class="'))[1].split('"')[0])
            break
        except:
            continue
    for page in range(number_pages):
        sleep(1)
        print(f"Page {page + 1} of {number_pages}")
        soup = grab_HTML("Seek", seek_url, page + 1)
        json_scripts = soup.find_all(
            'script', attrs={'type': 'application/ld+json'})
        json_data = json.loads(json_scripts[1].contents[0])
        # Extract location and status data.
        if parent_class != None:
            for optional_data in soup.find_all('div', attrs={'class': parent_class}):
                try:
                    location_data = optional_data.find(
                        'div', attrs={'id': 'work-location'})
                    locations.append(location_data.text)
                except:
                    locations.append("Unknown")
                status_data = optional_data.text
                if "current" in status_data:
                    status.append("Current")
                elif "former" in status_data:
                    status.append("Former")
                else:
                    status.append("Unknown")
        # Extract year, position, rating, and title data.
        for review in json_data['review']:
            year.append(review['datePublished'][:4])
            positions.append(review['author']['jobTitle'])
            ratings.append(review['reviewRating']['ratingValue'])
            titles.append(review['reviewBody'])
        # Extract review data.
        good_review, challenge_review = [], []
        for good_review_data in soup.find_all('div', attrs={'id': 'good-review'}):
            good_review.append(good_review_data.text[:-16])
        for challenge_review_data in soup.find_all('div', attrs={'id': 'challange-review'}):
            challenge_review.append(challenge_review_data.text[:-16])
        for review in range(len(good_review)):
            reviews.append(good_review[review] +
                           ". " + challenge_review[review])
    # If no status or location data exists, build correct Unknown list.
    if parent_class is None:
        status = ["Unknown"] * number_reviews
        locations = ["Unknown"] * number_reviews
    # Prepare and build CSV file.
    organisations = [organisation] * number_reviews
    website = ["Seek"] * number_reviews
    append_CSV(output_name, organisations, website, year, ratings,
               status, locations, positions, titles, reviews)
    print("Finished")

# Function: multi_review_scrape
def multi_scrape(websites, output_name, data=None):
    ''' Returns: Review data for multiple Indeed.com organisation as CSV files. '''
    # Load data from default file if none is supplied.
    if not data:
        with open("organisations.json") as content:
            data = json.load(content)
    # Read number seperate organisations to scrape.
    number_scrapes = len(data["configs"])
    print(f"Found {number_scrapes} organisation reviews to scrape ")
    for i in range(number_scrapes):
        config = data["configs"][i]
        organisation = config.get("organisation")
        # If true, only scrape from Indeed.
        if websites == "Indeed":
            indeed_url = config.get("indeed_url")
            indeed_country = config.get("indeed_country")
            print(f"Organisation {i + 1} of {number_scrapes}")
            indeed_scrape(organisation, indeed_url,
                          output_name, indeed_country)
        # If true, only scrape from Seek.
        elif websites == "Seek":
            seek_url = config.get("seek_url")
            print(f"Organisation {i + 1} of {number_scrapes}")
            seek_scrape(organisation, seek_url, output_name)
        # Scrape from both Seek and Indeed.
        elif websites == "Both":
            seek_url = config.get("seek_url")
            indeed_url = config.get("indeed_url")
            indeed_country = config.get("indeed_country")
            print(f"Organisation {i + 1} of {number_scrapes}")
            indeed_scrape(organisation, indeed_url,
                          output_name, indeed_country)
            seek_scrape(organisation, seek_url, output_name)
    print("All organisation scrapes finished")
