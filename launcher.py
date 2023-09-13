''' Created: 13/09/2023 '''

# External Dependencies
import inquirer
import re, os, sys

# Internal Dependencies
from scraper_controller import scrape_launch
from utilities.logger_formats import Log
from settings import CONFIG_DIRECTORY, OUTPUT_DIRECTORY

def list_filenames(directory: str, exclude: list[str] = [], include_extensions: bool = False) -> list[str]:
    ''' Returns: A list of strings of filenames for a specified directory,
        if include_extensions is true filenames include the filetype. Pass
        in exclude list to drop excluded options. Note, exclude check is 
        done with extensions present. '''
    filenames = os.listdir(directory)
    if exclude:
        filenames = [filename for filename in filenames if filename not in exclude]
    if not include_extensions:
        filenames = [os.path.splitext(filename)[0] for filename in filenames]
    return filenames

def prompt_filename(directory: str = None, prompt: str = None) -> str:
    ''' Returns: Filename str entered from user prompt. If user specifies
        a directory, this directory will be checked to ensure filename
        does not already exist, this check ignores filetypes. '''
    if prompt is None:
        prompt = 'Please enter a filename'
    while True:
        questions = [
            inquirer.Text('filename', message=prompt)
        ]
        answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
        filename = answer['filename']
        if not filename:
            Log.alert('You must provide a filename...')
        elif not re.match(r'^[^<>:"/\\|?*]+$', filename):
            Log.alert('Bad filename, avoid characters like <>:"/\\|?*.')
        elif directory is not None and filename in list_filenames(directory):
            Log.alert(f'A output file named {filename} already exists')
        else:
            return filename

def prompt_options(options: list[str], prompt: str = None) -> str:
    ''' Returns: Selected user option str from prompted list of options.
        Pass in a prompt str to modify the prompt prompt user sees. '''
    if not options or not isinstance(options, list):
        raise ValueError("Options should be a non-empty list.")
    if prompt is None:
        prompt = 'Please select an option:'
    questions = [
        inquirer.List('selection',
                      message=prompt,
                      choices=options,
                      )
    ]
    answer = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    return answer['selection']

if __name__ == '__main__':
    try:
        Log.status('Preparing to launch scraper...')
        output_name = prompt_filename(OUTPUT_DIRECTORY, 'Please specify a scraper results filename')
        scraper_options = list_filenames(CONFIG_DIRECTORY, ['.gitignore'], True)
        if not scraper_options:
            Log.alert(f'No available scraper configs. Create one at {CONFIG_DIRECTORY} first. ')
            sys.exit()
        config_file = prompt_options(scraper_options, 'Please select a scraper configuration')
        Log.status('Calling scraper launcher...')
        scrape_launch(config_file, output_name)
    except KeyboardInterrupt:
        Log.alert('Keyboard interrupt, aborting...')
        sys.exit()
