''' Creation Date: 09/11/2022 '''

# External Dependencies
from colorama import Fore, Style
import traceback
import pprint

# TODO: Modify Logging to take in error title and error body seperate. Initialise to only title or no logs.

class Log:
    ''' Purpose: Correctly format print messages given purpose. '''
    PREFIX_STATUS = f'[{Fore.GREEN}-{Style.RESET_ALL}]'
    PREFIX_INFO = f'{Fore.LIGHTBLACK_EX}[{Fore.BLUE}i{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL}'
    PREFIX_WARN = f'{Fore.LIGHTBLACK_EX}[{Fore.CYAN}*{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.CYAN}Warning:{Style.RESET_ALL}'
    PREFIX_ALERT = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}ALERT:{Style.RESET_ALL}'
    PREFIX_ERROR = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}ERROR:{Style.RESET_ALL}'
    PREFIX_TRACE = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}!{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}TRACE:{Style.RESET_ALL}'
    PREFIX_DUMP = f'{Fore.LIGHTBLACK_EX}[{Fore.RED}*{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}] {Fore.RED}DUMP:{Style.RESET_ALL}'
    @staticmethod
    def status(message: str):
        ''' Format: [-] message '''
        print(f'{Log.PREFIX_STATUS} {message}')
    @staticmethod
    def info(message: str):
        ''' Formats: [i] message '''
        print(f'{Log.PREFIX_INFO} {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}')
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
    def trace(error_traceback):
        ''' Formats: [!] TRACE: trace on next line '''
        formatted_traceback = ''.join(traceback.format_tb(error_traceback))
        print(f'{Log.PREFIX_TRACE}\n{Fore.LIGHTBLACK_EX}{formatted_traceback}{Style.RESET_ALL}')
    @staticmethod
    def dump(object):
        ''' Formats: [*] DUMP: dump on next line '''
        content = pprint.pformat(vars(object) if hasattr(object, '__dict__') else object)
        print(f'{Log.PREFIX_DUMP}\n{Fore.LIGHTBLACK_EX}{content}{Style.RESET_ALL}')
