''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
from bs4 import BeautifulSoup

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
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options)
    driver.implicitly_wait(10)
    return driver

def extract_blocks(page_html: str):
    ''' Returns: List of review data lists extracted from span text in HTML. '''
    soup = BeautifulSoup(page_html, 'html.parser')
    span_texts = [span.get_text() for span in soup.find_all('span')]
    try:
        blocks = []
        indices = [i for i, x in enumerate(span_texts) if x == 'The good things']
        for idx in indices:
            if idx - 4 >= 0 and idx + 3 < len(span_texts):
                blocks.append(span_texts[idx - 4: idx + 4])
        return blocks
    except:
        pass
        # Add something here...

def next_page(driver: webdriver.Chrome):
    ''' Returns: True or False if next page exists. '''
    try:
        # Try to find the "Next" button without tabindex="-1"
        driver.find_element(By.XPATH, "//a[@aria-label='Next' and not(@tabindex='-1')]")
        return True
    except:
        return False

def wait_for_change(driver: webdriver.Chrome, page_html: str):
    ''' Purpose: Checks page contents actually change, waits. '''
    wait = WebDriverWait(driver, 30)
    wait.until(lambda driver: driver.page_source != page_html)
    sleep(2)

def scrape_seek(driver: webdriver.Chrome, organisations: Organisations):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    total = 0
    for url in organisations.get_urls():
        driver.get(url)
        while True:
            page_html = driver.page_source
            blocks = extract_blocks(page_html)
            total += len(blocks)
            print(total)
            if next_page(driver):
                next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
                next_button.click()
                wait_for_change(driver, page_html)
            else:
                break
            # Appears to be a review mismatch, error exists, title missing from data.

def scrape_setup(scrape_file: str, debug: bool = False):
    ''' Purpose: Creates driver and data objects for scraping. '''
    driver = create_browser(debug)
    organisations = Organisations(scrape_file)
    organisations.display()
    scrape_seek(driver, organisations)

if __name__ == '__main__':
    scrape_setup('scrape_configs/test.json', debug = True)
