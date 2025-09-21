import re
import argparse
import logging
from abc import ABC, abstractmethod
import time
import functools
import os

#############################
###
###  HoI 4 Focus Localisation Adder, v2.0, created by Thanasis Lanaras
###  Written in Python 3.12.0
###
###    © Copyright 2023-2024 Thanasis Lanaras.
###    Licensed under the GNU Affero General Public License, Version 3.0 (the "License");
###
###    This program is free software: you can redistribute it and/or modify
###    it under the terms of the GNU Affero General Public License as published
###    by the Free Software Foundation, either version 3 of the License, or
###    (at your option) any later version.

###    This program is distributed in the hope that it will be useful,
###    but WITHOUT ANY WARRANTY; without even the implied warranty of
###    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###    GNU Affero General Public License for more details.
###    You should have received a copy of the GNU Affero General Public License
###    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#############################################################
###
### usage: focuslocadder.py [-h] -m {focus, idea, event} [-n] [-d] [-v] input output
### 
### Given an national focus, ideas or events file, it adds missing localisation entries
### to a specified localisation file. 
### Note: custom tooltips are not supported. (Planned for future)
### For it to find a focus, the id field should be **immediately after** 
### the focus = { line. Else, it won't be read.
### 
### Positional arguments:
###   -m, --mode  The type of file to process. (focus, idea, event)
###   input       National Focus/Idea/Event file to parse
###   output      Localisation file to write to (must be utf-8-bom)
### 
### Optional arguments:
###   -h, --help       show this help message and exit
###   -n, --find-names tries to locate the name of the focuses or events if they are commented, in the following way;
###                    focus = { # name here
###                    WARNING: CURRENTLY NOT IMPLEMENTED FOR IDEAS. IF AN IDEA ENTRY LOOKS LIKE THIS, THE PROGRAM WONT LOCALISE IT.
###   -d, --descs      If set, it will not generate desc keys.
###   -v, --verbose    If set, it will print debug messages.
###   -l, --newline    If set, will add a newline between every id-desc pair.
###
#############################################################


# DO NOT REMOVE -- THESE ARE USED FOR COLOURING THE LOG STATEMENTS
class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

class ColorFormatter(logging.Formatter):
    LOG_COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.MAGENTA,
    }
    
    def format(self, record):
        color = self.LOG_COLORS.get(record.levelno, LogColors.RESET)
        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"
        record.msg = f"{color}{record.msg}{LogColors.RESET}"
        return super().format(record)


def log_method_call(func):
    def wrapper(*args, **kwargs):
        logging.debug(f"Calling {func.__name__} with arguments {args} and keyword arguments {kwargs}")
        result = func(*args, **kwargs)
        logging.debug(f"{func.__name__} returned {result}")
        return result
    return wrapper

def elapsed_time(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds.")
        return result
    return wrapper

class LocAdder(ABC):
    """
    Base class for adding localization entries (focus, idea, event) to a localization file.

    This class provides the core logic for reading, parsing, and writing localization data
    into a specified file. Subclasses implement the details for extracting IDs from specific
    file types (focuses, ideas, events).

    Attributes:
        input_file (str): Path to the input file containing the focus/idea/event data.
        output_file (str): Path to the output localization file.
        find_names (bool): Flag indicating whether to find names for focuses if commented.
        mode (str): Mode indicating the type of file being processed (e.g., 'focus', 'idea', 'event').
        descs (bool): Flag indicating whether to include descriptions in the output.
        newline (bool): Flag indicating whether to add a newline between entries.
    """
    subclasses = { }
    
    def __init__(self, input_file: str, output_file: str, find_names: bool, descs: bool, mode: str, newline: bool) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.find_names = find_names
        self.mode = mode # focus, idea, or event
        self.descs = descs
        self.newline = newline
        
        if not self._process_paths():
            raise ValueError("Invalid input or output paths provided.")
        
        self.existing_content: str = self._read_file(self.output_file)
        
    @classmethod
    def register_subclass(cls, mode: str) -> callable:
        """Register a subclass for dynamic loading"""
        def decorator(subclass: type) -> type:
            cls.subclasses[mode] = subclass
            print(subclass)
            return subclass
        return decorator

    def _process_paths(self) -> bool:
        base_paths = {
            'focus': 'common/national_focus/',
            'idea': 'common/ideas/',
            'event': 'events/',
        }
        if self.mode in base_paths:
            self.input_file = f'{base_paths[self.mode]}{self.input_file}'
        else:
            logging.error(f"Invalid mode: {self.mode}")
            return False
        self.output_file = f'localisation/english/FX_country_specific/{self.output_file}'
        if not self.input_file.endswith('.txt') or not self.output_file.endswith('.yml'):
            logging.error("Input file must be a .txt file and output file must be a .yml file.")
            return False
        return True
    
    @classmethod
    def create(cls, mode, input_file, output_file, find_names, descs, newline):
        logging.debug(f"Creating subclass for mode: {mode}")
        subclass = cls.subclasses.get(mode)
        if not subclass:
            raise ValueError(f"Invalid mode: {mode}")
        return subclass(input_file, output_file, find_names, descs, mode, newline)

    
    def _read_file(self, path):
        """"Reads the content of a file if it exists"""
        if not os.path.exists(path):
            logging.error(f"File {path} does not exist. Creating a new file.")
            return ""
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
        
    def add_localisation_entries(self, entries):
        """Writes new localisation entries to the output file."""
        try:
            with open(self.output_file, 'a', encoding='utf-8-sig') as file:
                file.write('\n\n')
                for entry in entries:
                    if entry['id'] not in self.existing_content:
                        file.write(f'{entry["id"]}: "{entry["name"]}"\n')
                        
                        if self.descs and 'desc' in entry:
                            file.write(f'{entry["id"]}_desc: "{entry["desc"]}"\n')

                        if self.newline:
                            file.write('\n')
                        
                    else:
                        logging.debug(f"Skipping existing entry: {entry['id']}")
        except FileNotFoundError:
            logging.error(f"Output file {self.output_file} not found.")

    def add_event_localisation_entries(self, entries):
        """Writes new localisation entries to the output file."""
        try:
            with open(self.output_file, 'a', encoding='utf-8-sig') as file:
                file.write('\n\n')
                for entry in entries:
                    logging.debug(entry)
                    entry = {key: value.strip() if isinstance(value, str) else value for key, value in entry.items()} if isinstance(entry, dict) else entry
                    for key, value in entry.items():
                        if key == 'id' or key == 'options':
                            continue
                        if f'{key}:' not in self.existing_content:
                            file.write(f'{key}: "{value}"\n')
                        else:
                            logging.debug(f"Skipping existing entry: {key}")
                    
                    options = entry.get('options', {})
                    for option_key, option_value in options.items():
                        if f'{option_key}:' not in self.existing_content:
                            file.write(f'{option_key}: "{ option_value if option_value else "" }"\n')
                        else:
                            logging.debug(f"Skipping existing entry: {key}")
                    
                    if not self.newline:
                        continue
                    
                    if list(entry.keys())[2] not in self.existing_content:
                        logging.debug("Adding newline")
                        file.write('\n') 

        except FileNotFoundError:
            logging.error(f"Output file {self.output_file} not found.")
            
        except Exception as e:
            logging.error(f"An error occurred while writing to the output file: {e}")


    @abstractmethod
    def extract_ids(self):
        """Extracts IDs and optional names from the input file."""
        raise NotImplementedError("Subclasses must implement this method.")

    @elapsed_time
    def process_files(self):
        """Processes the input file and updates the output file."""
        entries = self.extract_ids()
        if self.mode != 'event':
            self.add_localisation_entries(entries)
        else:
            self.add_event_localisation_entries(entries)
        logging.info(f"{self.mode.capitalize()} file successfully updated.")

@LocAdder.register_subclass('focus')
class FocusLocAdder(LocAdder):
    @log_method_call
    def extract_ids(self):
        focus_ids = []
        inside_focus = False
        possible_names = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                for line in file:
                    if 'focus = {' in line:
                        inside_focus = True
                        if '#' in line:
                            possible_name = line.split('#', 1)[1].strip()
                            possible_names.append(possible_name.replace("'", "\\'"))
                    elif inside_focus and '}' in line:
                        inside_focus = False
                    elif inside_focus and 'id =' in line:
                        focus_id = re.search(r'id = (.*?)\s', line)
                        if focus_id:
                            focus_ids.append({
                                'id': focus_id.group(1).strip('"'), 
                                'name': possible_names[-1] if self.find_names else '',
                                'desc': ''
                            })
                            inside_focus = False  # Set inside_focus to False after extracting the ID
                        else:
                            logging.warning(f"Malformed 'id' field in line: {line.strip()}")
        except FileNotFoundError:
            logging.error(f"File not found: {self.input_file}")
        return focus_ids

@LocAdder.register_subclass('idea')
class IdeaLocAdder(LocAdder):
    
    @log_method_call
    def extract_ids(self):
        idea_ids = []
        inside_country_block = False
        brace_level = 0  # To track nested braces
        # possible_names = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                for line in file:
                    stripped_line = line.strip()

                    # Skip comment lines
                    if stripped_line.startswith('#'):
                        continue

                    # Enter the "country" block
                    if 'country = {' in stripped_line:
                        inside_country_block = True
                        brace_level = 1
                        continue

                    # If inside the "country" block, adjust brace level
                    if inside_country_block:
                        brace_level += stripped_line.count('{') - stripped_line.count('}')
                        if brace_level == 0:  # Exit the "country" block
                            inside_country_block = False
                            continue

                        # Detect idea blocks
                        if '=' in stripped_line and '{' in stripped_line and brace_level == 2:
                            left_part = stripped_line.split('=', 1)[0].strip()
                            if stripped_line.endswith('{'):
                                if re.match(r'^[A-Za-z0-9_]+$', left_part):
                                    idea_ids.append({
                                        'id': left_part,
                                        'name': '', #possible_names[-1] if self.find_names else '',
                                        'desc': ''
                                    })
                                    # if '#' in line:
                                    #     possible_name = line.split('#', 1)[1].strip()
                                    #     possible_names.append(possible_name)

        except FileNotFoundError:
            logging.error(f"File not found: {self.input_file}")

        return idea_ids


@LocAdder.register_subclass('event')
class EventLocAdder(LocAdder):
    
    @log_method_call
    def extract_ids(self):
        event_data = []
        current_event = None
        inside_event_block = False
        brace_level = 0
        last_comment = None
        inside_option_block = False

        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i in range(1, len(lines)):
                    curr_line = lines[i]
                    prev_line = lines[i - 1]
                    
                    stripped_line = curr_line.strip()

                    # Skip comment lines
                    if stripped_line.startswith('#'):
                        # last_comment = stripped_line[1:].strip()
                        # logging.debug(f"Comment: {last_comment}")
                        
                        continue

                    
                    # Handle country_event block start
                    elif 'country_event = {' in stripped_line:
                        if prev_line.startswith('#'):
                            last_comment = prev_line.split('#', 1)[1].strip().replace("'", "\\'")
                            logging.debug(f"Comment: {last_comment}")
                        inside_event_block = True
                        brace_level = 1
                        current_event = {
                            'id': None,
                            'options': {}
                        }
                        # Inline comment (prefer this over the previous line's comment if both exist)
                        if '#' in curr_line:
                            last_comment = curr_line.split('#', 1)[1].strip().replace("'", "\\'")
                            logging.debug(f"Inline comment: {last_comment}")

                    elif inside_event_block:
                        brace_level += stripped_line.count('{') - stripped_line.count('}')
                        if brace_level == 0:
                            inside_event_block = False
                            if current_event['id']:
                                event_data.append(current_event)
                            current_event = None 
                            continue
                        
                        if 'id =' in stripped_line and not current_event['id']:
                            match = re.search(r'id = (\S+)', stripped_line)
                            if match:
                                current_event['id'] = match.group(1)

                        if 'title =' in stripped_line:
                            match = re.search(r'title = (\S+)', stripped_line)
                            if match:
                                current_event[match.group(1)] = last_comment or ''
                                last_comment = None

                        if 'desc =' in stripped_line:
                            match = re.search(r'desc = (\S+)', stripped_line)
                            if match:
                                current_event[match.group(1)] = last_comment or ''
                                # last_comment = None
                        
                        if 'option = {' in stripped_line:
                            inside_option_block = True
                            if '#' in curr_line:
                                last_comment = curr_line.split('#', 1)[1].strip().replace("'", "\\'")
                                logging.debug(f"Inline comment: {last_comment}")
                            continue
                        
                        if inside_option_block:
                            if 'name =' in stripped_line:
                                match = re.search(r'name = (\S+)', stripped_line)
                                if match:
                                    option_id = match.group(1)
                                    current_event['options'][option_id] = last_comment or ''
                                    last_comment = None
                                    # curr_option_name = None
                            if '}' in stripped_line:  # End of option block
                                inside_option_block = False

        except FileNotFoundError:
            logging.error(f"File not found: {self.input_file}")

        return event_data



def main():
    parser = argparse.ArgumentParser(description='Given a national focus, ideas, or events file, it adds missing localisation entries to a specified localisation file. Note: custom tooltips are not supported. (Planned for future) For it to find a focus, the id field should be **immediately after**  the focus = { line. Else, it won\'t be read.')
    parser.add_argument('-m', '--mode', choices=LocAdder.subclasses.keys(), required=True, help='The type of file to process.') 
    parser.add_argument('input_file', help='Path to the input file.')
    parser.add_argument('output_file', help='Path to the output file.')
    parser.add_argument('-n', '--find-names', action='store_true', required=False, default=False, help="tries to locate the name of the focuses if they are commented, in the following way; focus = { name here)")
    parser.add_argument('-d', '--descs', action='store_false', required=False, default=True, help="If set, it will not generate desc keys.")
    parser.add_argument('-v', '--verbose', action='store_true', required=False, default=False, help="If set, it will print debug messages.")
    parser.add_argument('-l', '--newline', action='store_true', required=False, default=False, help="If set, will add a newline between every id-desc pair.")
    args = parser.parse_args()

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    logging.debug(f"Mode: {args.mode}, Input File: {args.input_file}, Output File: {args.output_file}")
    
    try:
        adder = LocAdder.create(args.mode, args.input_file, args.output_file, args.find_names, args.descs, args.newline)
        adder.process_files()
    except ValueError as e:
        logging.error(e)

if __name__ == "__main__":
    main()
