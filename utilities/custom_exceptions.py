''' Created: 11/09/2023 '''

# External Dependencies
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

# Internal Dependencies
from utilities.logger_formats import Log

class ScraperExceptions:
    ''' Purpose: Stores all custom exception logic for project. '''
    class InvalidConfigFile(Exception):
        ''' Exception: JSON file was not valid. '''
        pass
    class BadSettings(Exception):
        ''' Exception: The settings.yml file has wrong type value. '''
        pass
    class UnexpectedData(Exception):
        ''' Exception: Scraped data was not as Scraper class expected. '''
        pass
    class NavigationFail(Exception):
        ''' Exception: Selenium Browser failed to navigate, check internet. '''
        pass
    class BadScraper(Exception):
        ''' Exception: Dynamic scraper function returned invalid type. '''
        pass
    def handle_non_critical(func, data_strict: bool, *args, **kwargs):
        ''' Purpose: Handles non-critical functions given config.data_strict setting. 
            Will allow a wrapped function to fail and return none if not strict. '''
        try:
            return func(*args, **kwargs)
        except Exception as e:
            Log.alert(f'Failed to get value!\n{e}')
            if data_strict:
                raise ScraperExceptions.UnexpectedData('Settings on data_strict True, aborting...')
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                return None
    def handle_bad_data(func, data_strict: bool, *args, **kwargs):
        ''' Purpose: Handles bad data given config.data_strict setting. Will
            allow a wrapped function to not validate and continue if not strict.'''
        try:
            func(*args, **kwargs)
        except ScraperExceptions.UnexpectedData as e:
            Log.alert(f'Potential bad data!\n{e.args[0]}')
            if data_strict:
                raise ScraperExceptions.UnexpectedData('Settings on data_strict True, aborting...')
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
    def handle_bad_nav(func, *args, **kwargs):
        ''' Purpose: Whilst entry navigator functions should use dynamic waits,
            this allows a wrapped navigator to race and will retry up to 5 times. '''
        fails = 0
        while fails < 5:
            try:
                return func(*args, **kwargs)
            except (StaleElementReferenceException, TimeoutException, NoSuchElementException) as e:
                Log.warn(f'Navigation failed, retrying: {fails}')
                fails += 1
                if fails >= 5:
                    raise ScraperExceptions.NavigationFail(e)
            except Exception as e:
                raise ScraperExceptions.NavigationFail(e)
