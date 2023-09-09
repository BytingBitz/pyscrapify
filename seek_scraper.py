''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from utility import Log
import re

PATTERN = r'https?://www\.seek\.com\.au/companies/.+/reviews'

class Organisations:
    ''' Purpose: Load scrape_config for scraping. '''
    def __init__(self, json_file_path):
        self.organisations = []
        self.load_from_json(json_file_path)
    def load_from_json(self, json_file_path):
        ''' Purpose: Loads JSON to object. '''
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for name, url in data['organisations'].items():
                self.organisations.append({'name': name, 'url': url})
    def get_urls(self):
        ''' Returns: List of organisation URLs. '''
        return [org['url'] for org in self.organisations]
    def display(self):
        ''' Purpose: Displays loaded organisations. '''
        for org in self.organisations:
            print(f'{org["name"]}: {org["url"]}')

def create_browser(debug: bool = False):
    ''' Returns: Selenium browser session. '''
    options = webdriver.ChromeOptions()
    if not debug:
        options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Comment for logs
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options)
    driver.implicitly_wait(10)
    return driver

def extract_data(page_html: str):
    ''' Returns: List of review data lists extracted from HTML text. '''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = [element.get_text() for element in soup.find_all(['span', 'h3'])]
    data = []
    indices = [i for i, x in enumerate(texts) if x == 'The good things']
    for idx in indices:
        if idx - 5 >= 0 and idx + 3 < len(texts):
            data.append(texts[idx - 5: idx + 4])
    return data

def next_page(driver: webdriver.Chrome):
    ''' Returns: True or False if next page exists. '''
    try:
        # Try to find the "Next" button without tabindex="-1"
        driver.find_element(By.XPATH, "//a[@aria-label='Next' and not(@tabindex='-1')]")
        return True
    except:
        return False

def scrape_data(driver: webdriver.Chrome):
    ''' Returns: All reviews scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html))
        if next_page(driver):
            pbar.update(1)
            next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
            next_button.click()
            wait = WebDriverWait(driver, 30)
            wait.until(lambda driver: driver.page_source != page_html)
            sleep(3)
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_seek(driver: webdriver.Chrome, organisations: Organisations):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for url in organisations.get_urls():
        Log.status(f'Scraping {url}')
        try:
            if not re.match(PATTERN, url):
                Log.alert(f'Provided URL is not a valid Seek company reviews link...\n{url}')
                failed.append(name)
                continue
            driver.get(url)
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))
        except TimeoutException:
            Log.alert(f'Failed to get {name}, check URL or internet...\n{url}')
            failed.append(name)
            continue
        try:
            review_data = scrape_data(driver)
            if len(review_data) != total_reviews:
                Log.alert(f'Mismatch between expected and actual {name} reviews...')
                failed.append(name)
                continue
        except:
            pass        

def scrape_launch(scrape_file: str, debug: bool = False):
    ''' Purpose: Creates driver and data objects for scraping. '''
    driver = None
    try:
        driver = create_browser(debug)
        organisations = Organisations(scrape_file)
        organisations.display()
        scrape_seek(driver, organisations)
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            Log.alert('Keyboard interrupt, aborting...')
        else:
            Log.alert(f'Unexpected error occurred...\n{e}')
    finally:
        if driver:
            driver.quit()
        exit(0)

if __name__ == '__main__':
    Log.info('Debug test, browser has header...')
    scrape_launch('scrape_configs/test.json', debug=True)
