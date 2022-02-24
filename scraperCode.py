from bs4 import BeautifulSoup
import urllib.request as lib
from time import sleep
from math import ceil
from tqdm import tqdm
import os.path
import json
import csv
import re


months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def dictionary_build():
    return {
        'organisation': [],
        'website': [],
        'year': [],
        'month': [],
        'day': [],
        'country': [],
        'rating': [],
        'status': [],
        'location': [],
        'position': [],
        'title': [],
        'review': [],
        'pro': [],
        'con': []
    }


def grab_HTML(website, seek_url, start, country=None):
    ''' Returns: Selected webpage soup. '''
    for _ in range(15):
        try:
            if website == "Indeed":
                req = lib.Request(f'{seek_url}?start='+str(start)+'&fcountry='+country,
                                  headers={'User-Agent': 'Mozilla/5.0'})
            else:
                req = lib.Request(f'{seek_url}?page=' + str(start),
                                  headers={'User-Agent': 'Mozilla/5.0'})
            webpage = lib.urlopen(req)
            return BeautifulSoup(webpage, 'html.parser')
        except:
            sleep(5)
            continue
    print("Failed to grab HTML")
    exit(0)


def data_validation(values, length, number_reviews):
    ''' Validates data meets criteria. '''
    if all(len(item) == length for item in values):
        print("Values length match check passed")
    else:
        print("Values length test failed, read failure")
        exit(0)
    if length == number_reviews:
        print("Expected reviews count check passed")
    else:
        print("Expected length test failed, read failure")
        exit(0)


def append_CSV(filename, dic, number_reviews):
    ''' Returns: Built and named CSV file containing firm review data. '''
    if not filename.endswith(".csv"):
        filename += ".csv"
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        if not file_exists:
            headers = ["Organisation", "Website", "Country", "Year", "Month", "Day", "Rating",
                       "Status", "Location", "Position", "Title", "Review", "Pros", "Cons"]
            writer.writerow(headers)
        values = dic.values()
        length = len(dic['organisation'])
        data_validation(values, length, number_reviews)
        for i in range(length):
            writer.writerow([
                dic['organisation'][i],
                dic['website'][i],
                dic['country'][i],
                dic['year'][i],
                dic['month'][i],
                dic['day'][i],
                dic['rating'][i],
                dic['status'][i],
                dic['location'][i],
                dic['position'][i],
                repr(dic['title'][i])[1:-1],
                repr(dic['review'][i])[1:-1],
                dic['pro'][i],
                dic['con'][i]]
            )


def review_volume(soup, website, reviews_per_page):
    ''' Returns: Detected number reviews and number pages of reviews on website. '''
    try:
        if website == "Indeed":
            overview_data = soup.find(
                'div', attrs={'data-testid': 'review-count'})
            try:
                number_reviews = int(overview_data.find(
                    'span').find('b').text.replace(',', ''))
            except:
                number_reviews = int(re.findall(
                    r'\d+', overview_data.find('span').text)[0])
            number_pages = ceil((number_reviews - 1) / reviews_per_page)
        elif website == "Seek":
            overview_data = soup.find('div', attrs={'id': 'app'})
            number_reviews = int((overview_data.text.split(
                "ReviewOverviewReviews"))[1].split("JobsTop")[0])
            number_pages = ceil((number_reviews) / reviews_per_page)
        return number_reviews, number_pages
    except:
        print(f"Failed to determine {website} review volume")
        exit(0)


def indeed_position(big_soup, page, indeed_url, indeed_country, reviews_per_page):
    ''' Returns: Review specific soup and index. '''
    if page == 0:
        soup, jump = big_soup, 0
    else:
        soup, jump = grab_HTML("Indeed", indeed_url,
                               page * reviews_per_page, indeed_country), 1
    return soup, jump


def indeed_heading(soup, jump, dic):
    ''' Returns: Extracted review Indeed header data. '''
    author_text = []
    for author_data in soup.find_all('span', attrs={'itemprop': 'author'})[jump:]:
        dic['position'].append(author_data.find('meta').attrs['content'])
        author_text.append(author_data.text)
    for author_entry in author_text:
        split_data = author_entry.rsplit(' - ', 2)
        if "(Current Employee)" in split_data[0]:
            dic['status'].append("Current")
        else:
            dic['status'].append("Former")
        dic['location'].append(split_data[1])
        time_data = split_data[2].split()
        dic['year'].append(time_data[2])
        dic['month'].append(time_data[1])
        dic['day'].append(time_data[0])
    return dic


def indeed_body(soup, jump, dic):
    ''' Returns: Extracted review Indeed body data. '''
    for rating_data in soup.find_all('div', attrs={'itemprop': 'reviewRating'})[jump:]:
        dic['rating'].append(rating_data.find('meta').attrs['content'])
    for title_data in soup.find_all('h2', attrs={'data-testid': 'title'})[jump:]:
        dic['title'].append(title_data.text)
    for review_data in soup.find_all('span', attrs={'itemprop': 'reviewBody'})[jump:]:
        dic['review'].append(review_data.text)
    return dic


def indeed_footer(soup, jump, dic):
    ''' Returns: Extracted review Indeed footer data. '''
    for procon_data in soup.find_all('div', attrs={'itemprop': 'review'})[jump:]:
        try:
            dic['pro'].append(procon_data.find(
                'h2', string='Pros').next_sibling.text)
        except:
            dic['pro'].append("")
        try:
            dic['con'].append(procon_data.find(
                'h2', string='Cons').next_sibling.text)
        except:
            dic['con'].append("")
    return dic


def indeed_csv(filename, firm, indeed_country, number_reviews, dic):
    ''' Completes Indeed dictionary population. '''
    dic['organisation'] = [firm] * number_reviews
    dic['website'] = ["Indeed"] * number_reviews
    dic['country'] = [indeed_country] * number_reviews
    append_CSV(filename, dic, number_reviews)
    print("Indeed finished")


def indeed_scrape(firm, indeed_url, filename, indeed_country):
    ''' Scrapes all review data for given Indeed config. '''
    print("Scraping Indeed reviews")
    big_soup = grab_HTML("Indeed", indeed_url, 0, indeed_country)
    dic = dictionary_build()
    reviews_per_page = 20
    number_reviews, number_pages = review_volume(
        big_soup, "Indeed", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    for page in tqdm(range(number_pages)):
        sleep(0.5)
        soup, jump = indeed_position(
            big_soup, page, indeed_url, indeed_country, reviews_per_page)
        dic = indeed_heading(soup, jump, dic)
        dic = indeed_body(soup, jump, dic)
        dic = indeed_footer(soup, jump, dic)
    indeed_csv(filename, firm, indeed_country, number_reviews, dic)


def seek_position(number_pages, seek_url):
    ''' Returns: Review specific soup and parent class. '''
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
    return optional_data, parent_class


def seek_header(soup, dic, parent_class, optional_data):
    ''' Returns: Extracted review Seek header data. '''
    if parent_class is None:
        return
    for optional_data in soup.find_all('div', attrs={'class': parent_class}):
        try:
            location_data = optional_data.find(
                'div', attrs={'id': 'work-location'})
            dic['location'].append(location_data.text)
        except:
            dic['location'].append("Unknown")
        status_data = optional_data.text
        if "current" in status_data:
            dic['status'].append("Current")
        elif "former" in status_data:
            dic['status'].append("Former")
        else:
            dic['status'].append("Unknown")
    return dic


def seek_body(soup, dic):
    ''' Returns: Extracted review Seek body data. '''
    json_scripts = soup.find_all(
        'script', attrs={'type': 'application/ld+json'})
    json_data = json.loads(json_scripts[1].contents[0])
    for review in json_data['review']:
        time_data = review['datePublished'].split("-")
        dic['year'].append(time_data[0])
        dic['month'].append(months[int(time_data[1])])
        dic['day'].append(time_data[2])
        dic['position'].append(review['author']['jobTitle'])
        dic['rating'].append(review['reviewRating']['ratingValue'])
        dic['title'].append(review['reviewBody'])
    return dic


def seek_footer(soup, dic):
    ''' Returns: Extracted review Seek footer data. '''
    for good_review_data in soup.find_all('div', attrs={'id': 'good-review'}):
        dic['pro'].append(' '.join(good_review_data.text[:-16].split()))
    for challenge_review_data in soup.find_all('div', attrs={'id': 'challange-review'}):
        dic['con'].append(' '.join(challenge_review_data.text[:-16].split()))
    return dic


def seek_csv(filename, firm, parent_class, number_reviews, dic):
    ''' Completes Seek dictionary population. '''
    if parent_class is None:
        dic['status'] = ["Unknown"] * number_reviews
        dic['location'] = ["Unknown"] * number_reviews
    dic['organisation'] = [firm] * number_reviews
    dic['website'] = ["Seek"] * number_reviews
    dic['country'] = ["AU"] * number_reviews
    dic['review'] = [""] * number_reviews
    append_CSV(filename, dic, number_reviews)
    print("Seek finished")


def seek_scrape(firm, seek_url, filename):
    ''' Scrapes all review data for given Seek config. '''
    print("Scraping Seek reviews")
    big_soup = grab_HTML("Seek", seek_url, 1)
    reviews_per_page = 10
    dic = dictionary_build()
    number_reviews, number_pages = review_volume(
        big_soup, "Seek", reviews_per_page)
    print(f"Found {number_reviews} reviews")
    optional_data, parent_class = seek_position(number_pages, seek_url)
    for page in tqdm(range(number_pages)):
        sleep(0.5)
        soup = grab_HTML("Seek", seek_url, page + 1)
        dic = seek_header(soup, dic, parent_class, optional_data)
        dic = seek_body(soup, dic)
        dic = seek_footer(soup, dic)
    seek_csv(filename, firm, parent_class, number_reviews, dic)


def execute_indeed(config, count: int, number_scrapes: int, name: str):
    ''' Returns: Specified Indeed Organisation Scrape. '''
    firm = config.get("organisation")
    indeed_url = config.get("indeed_url")
    indeed_country_list = config.get("indeed_country")
    if isinstance(indeed_country_list, str):
        indeed_country_list = [indeed_country_list]
    print(f"Organisation {count + 1} of {number_scrapes}")
    for indeed_country in indeed_country_list:
        if indeed_url is not None and indeed_country is not None:
            indeed_scrape(firm, indeed_url, name, indeed_country)
        else:
            print(f"Indeed skipped for firm {count + 1} of {number_scrapes}")


def execute_seek(config, count: int, number_scrapes: int, name: str):
    ''' Returns: specified seek organisation scrape. '''
    firm = config.get("organisation")
    seek_url = config.get("seek_url")
    if seek_url is not None:
        print(f"Organisation {count + 1} of {number_scrapes}")
        seek_scrape(firm, seek_url, name)
    else:
        print(f"Seek skipped for firm {count + 1} of {number_scrapes}")


def execute_both(config, count: int, number_scrapes: int, name: str):
    ''' Returns: Specified Indeed and Seek Organisation Scrapes'''
    execute_indeed(config, count, number_scrapes, name)
    execute_seek(config, count, number_scrapes, name)


def multi_scrape(websites, name):
    ''' Returns: Review data for multiple firm as CSV files. '''
    with open("organisations.json") as content:
        data = json.load(content)
    number_scrapes = len(data["configs"])
    print(f"Found {number_scrapes} firm reviews to scrape")
    for i in range(number_scrapes):
        config = data["configs"][i]
        if websites == "Indeed":
            execute_indeed(config, i, number_scrapes, name)
        elif websites == "Seek":
            execute_seek(config, i, number_scrapes, name)
        elif websites == "Both":
            execute_both(config, i, number_scrapes, name)
    print("All firm scrapes finished")
