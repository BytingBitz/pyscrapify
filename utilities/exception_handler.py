''' Created: 11/09/2023 '''

from utilities.logger_formats import Log

class ScraperExceptions:
    ''' Purpose: Stores all custom exception logic for project. '''
    class InvalidJsonFormat(Exception):
        ''' Exception: JSON file was not valid. '''
        pass
    class UnexpectedData(Exception):
        ''' Exception: Scraped data was not as Scraper class expected. '''
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
