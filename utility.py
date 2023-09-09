''' Creation Date: 09/11/2022 '''

from colorama import Fore, Style

# Stores general classes and functions used across project

class Log:
    ''' Purpose: Correctly format print messages given purpose. '''
    def status(message: str):
        ''' Format: [-] message'''
        indicator = '[' + Fore.GREEN + '-' + Style.RESET_ALL + ']'
        print(f'{indicator} {message}...')
    def alert(message: str):
        ''' Format: [!] message'''
        indicator = '[' + Fore.RED + '!' + Style.RESET_ALL + ']'
        print(f'{indicator} {message}...')
    def info(message: str):
        ''' Formats: [i] message'''
        indicator = '[' + Fore.BLUE + 'i' + Style.RESET_ALL + ']'
        print(f'{indicator} {message}...')
