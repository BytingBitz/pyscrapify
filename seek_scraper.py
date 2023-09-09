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
import traceback

PATTERN = r'https?://www\.seek\.com\.au/companies/.+/reviews'

class Config_JSON:
    ''' Purpose: Load specified scrape_config contents. '''
    # Missing code to verify JSON file contents/existence
    def __init__(self, json_file_path):
        self.orgs = []
        self.load_orgs(json_file_path)
    def load_orgs(self, json_file_path):
        ''' Purpose: Creates organisations, list of URL and name dictionaries. '''
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for name, url in data['organisations'].items():
                self.orgs.append({'name': name, 'url': url})
    def get_orgs(self) -> list:
        ''' Returns: List of organisation names and URLs. '''
        return [(org['name'], org['url']) for org in self.orgs]
    def string(self) -> str:
        ''' Returns: String of organisation names and URLs. '''
        return '\n'.join([f'{org["name"]}: {org["url"]}' for org in self.orgs])

def create_browser(debug: bool = False) -> webdriver:
    ''' Returns: Created Selenium Chrome browser session. '''
    options = webdriver.ChromeOptions()
    if not debug:
        options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Comment for logs
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options)
    driver.implicitly_wait(10)
    return driver

def extract_data(page_html: str) -> list:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = [element.get_text() for element in soup.find_all(['span', 'h3'])]
    data = []
    indices = [i for i, x in enumerate(texts) if x == 'The good things']
    for idx in indices:
        if idx - 5 >= 0 and idx + 3 < len(texts):
            data.append(texts[idx - 5: idx + 4])
    return data

def next_page(next_button: webdriver.Remote._web_element_cls) -> bool:
    ''' Returns: Boolean True or False if next page is accessible. '''
    return next_button.get_attribute("tabindex") != "-1"

def scrape_data(driver: webdriver.Chrome) -> list:
    ''' Returns: List of lists of all reviews data scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html))
        next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        if next_page(next_button):
            next_button.click()
            wait = WebDriverWait(driver, 30)
            wait.until(lambda driver: driver.page_source != page_html)
            sleep(3) # Find more robust next page verification
            pbar.update(1)
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_seek(driver: webdriver.Chrome, config_json: Config_JSON):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for name, url in config_json.get_orgs():
        Log.status(f'Scraping {name}')
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
        #try:
        review_data = scrape_data(driver)
            # Add way to source total_reviews
            # if len(review_data) != total_reviews:
            #     Log.alert(f'Mismatch between expected and actual {name} reviews...')
            #     failed.append(name)
            #     continue
        #except: # Incomplete, requires explicit exception handling
        #    pass        

def scrape_launch(scrape_file: str, debug: bool = False):
    ''' Purpose: Creates driver and data objects for scraping. '''
    driver = None
    try:
        driver = create_browser(debug)
        config_json = Config_JSON(scrape_file)
        Log.info(f'Loaded {scrape_file} contents:\n{config_json.string()}')
        scrape_seek(driver, config_json)
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            Log.alert('Keyboard interrupt, aborting...')
        else:
            Log.alert(f'Unexpected error occurred...\n{e}')
            traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        exit(0)

if __name__ == '__main__':
    Log.info('Debug test, browser has header...')
    scrape_launch('scrape_configs/test.json', debug=True)
