''' Creation Date: 09/11/2022 '''

from scraper_logic import ScrapeConfig
from colorama import Fore, Style
import traceback

WEBDRIVER_TIMEOUT = 20

# TODO: Modify Logging to take in error title and error body seperate. Initialise to only title or no logs.

class Log:
    ''' Purpose: Correctly format print messages given purpose. '''
    PREFIX_STATUS = f'[{Fore.GREEN}-{Style.RESET_ALL}]'
    PREFIX_WARN = f'{Fore.LIGHTBLACK_EX}[{Fore.CYAN}*{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.CYAN}Warning:{Style.RESET_ALL}'
    PREFIX_ALERT = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}Alert:{Style.RESET_ALL}'
    PREFIX_ERROR = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}ERROR:{Style.RESET_ALL}'
    PREFIX_INFO = f'{Fore.LIGHTBLACK_EX}[{Fore.BLUE}i{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL}'
    PREFIX_TRACE = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}TRACE:{Style.RESET_ALL}'
    @staticmethod
    def status(message: str):
        ''' Format: [-] message '''
        print(f'{Log.PREFIX_STATUS} {message}')
    @staticmethod
    def warn(message: str):
        ''' Format: [*] Warning: message '''
        print(f'{Log.PREFIX_WARN} {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}')
    @staticmethod
    def alert(message: str):
        ''' Format: [!] Alert: message '''
        print(f'{Log.PREFIX_ALERT} {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}')
    @staticmethod
    def error(message: str):
        ''' Format: [!] ERROR: message '''
        print(f'{Log.PREFIX_ERROR} {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}')
    @staticmethod
    def info(message: str):
        ''' Formats: [i] message '''
        print(f'{Log.PREFIX_INFO} {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}')
    @staticmethod
    def trace(error_traceback):
        ''' Formats: [!] Trace: trace on next line '''
        formatted_traceback = ''.join(traceback.format_tb(error_traceback))
        print(f'{Log.PREFIX_TRACE}\n{Fore.LIGHTBLACK_EX}{formatted_traceback}{Style.RESET_ALL}')

class ScraperExceptions:
    ''' Purpose: Stores all custom exception logic for project. '''
    class InvalidJsonFormat(Exception):
        ''' Exception: JSON file was not valid. '''
        pass
    class UnexpectedData(Exception):
        ''' Exception: scraped data was not as expected. '''
        pass
    def handle_non_critical(func, config: ScrapeConfig, *args, **kwargs):
        ''' Purpose: Handles non-critical functions given config.data_strict setting. 
            Will allow a wrapped function to fail and return none if not strict. '''
        try:
            return func(*args, **kwargs)
        except Exception as e:
            Log.alert(f'Failed to get value!\n{e}')
            if config.data_strict:
                raise ScraperExceptions.UnexpectedData('Settings on data_strict True, aborting...')
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                return None
    def handle_bad_data(func, config: ScrapeConfig, *args, **kwargs):
        ''' Purpose: Handles bad data given config.data_strict setting. Will
            allow a wrapped function to not validate and continue if not strict.'''
        try:
            func(*args, **kwargs)
        except ScraperExceptions.UnexpectedData as e:
            Log.alert(f'Potential bad data!\n{e.args[0]}')
            if config.data_strict:
                raise ScraperExceptions.UnexpectedData('Settings on data_strict True, aborting...')
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
