''' Created: 12/09/2023 '''

# External Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from requests.exceptions import ChunkedEncodingError

# Internal Dependencies
from utilities.logger_formats import Log

class BrowserManager:
    def __init__(self, language: str, header: bool = False, logging: bool = False):
        self.header = header
        self.logging = logging
        self.language = language
    def create_browser(self) -> WebDriver:
        ''' Returns: Created Selenium Chrome browser session. '''
        options = webdriver.ChromeOptions()
        options.add_argument(f'--lang={self.language}')
        if not self.header:
            Log.info('Running Selenium driver without header...')
            options.add_argument('--headless')
        if not self.logging:
            Log.info('Disabled Selenium driver logging...')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options)
            return driver
        except (ChunkedEncodingError, TimeoutException) as e:
            raise ConnectionError(f'Failed due to {type(e).__name__}: check internet and try again.')
    def __enter__(self):
        self.driver = self.create_browser()
        return self.driver
    def __exit__(self, exc_type, *_):
        if exc_type is None:
            Log.info('Ending Selenium driver session...')
        else:
            Log.alert('Error occurred, ending Selenium driver session...')
        self.driver.quit()
