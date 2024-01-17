import re
import argparse
import logging
from pathlib import Path

#############################
###
### HoI 4 Focus Localisation Adder, created by Thanasis Lanaras
### Written in Python 3.12.0
###
###    Copyright (C) 2024 Thanasis Lanaras.
###
### This program is free software: you can redistribute it and/or modify
### it under the terms of the GNU Affero General Public License as published
### by the Free Software Foundation, version 3 of the License.

### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU Affero General Public License for more details.

#############################################################
###
### usage: focuslocadder.py [-h] input output
### 
### Given an national focus file, it adds missing localisation entries
### to a specified localisation file. 
### Note: custom tooltips are not supported. (Planned for future)
### For it to find a focus, the id field should be **immediately after** 
### the focus = { line. Else, it won't be read.
### The script also automatically finds the id (or desc) loc key (if they exist) and adds the desc key after the id
### (or the id key before the desc)
### 
### Positional arguments:
###   input       National Focus file to parse
###   output      Localisation file to write to (must be utf-8-bom)
### 
### Optional arguments:
###   -h, --help  show this help message and exit
###
#############################################################

class FocusLocAdder:
    def __init__(self, input_file, output_file):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)

    def extract_focus_ids(self):
        focus_ids = []
        inside_focus = False
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                for line in file:
                    if 'focus = {' in line:
                        inside_focus = True
                    elif inside_focus and '}' in line:
                        inside_focus = False
                    elif inside_focus and 'id =' in line:
                        focus_id = re.search(r'id = (.*?)\s', line)
                        if focus_id:
                            focus_ids.append(focus_id.group(1).strip('"'))
                            inside_focus = False  # Set inside_focus to False after extracting the ID
                        else:
                            logging.warning(f"Malformed 'id' field in line: {line.strip()}")
        except FileNotFoundError:
            logging.error(f"File not found: {self.input_file}")
        return focus_ids

    def update_output_file(self):
        focus_ids = self.extract_focus_ids()

        try:
            with open(self.output_file, 'a', encoding='utf-8-sig') as file:
                newline_added = False
                for focus_id in focus_ids:
                    id_entry = f'{focus_id}: ""\n'
                    desc_entry = f'{focus_id}_desc: ""\n'

                    with open(self.output_file, 'r', encoding='utf-8') as output_file_reader:
                        content = output_file_reader.read()
                        if focus_id not in content:
                            if content.strip() and not newline_added:
                                file.write('\n')
                                newline_added = True
                            file.write(id_entry)
                        if f'{focus_id}_desc' not in content:
                            file.write(desc_entry)
        except FileNotFoundError:
            logging.error(f"File not found: {self.output_file}")

    def process_files(self):
        self.update_output_file()
        logging.info("Focus tree file successfully updated.")

# If you're reading the code and wonder what this does here, it is something I plan for the future but doesn't quite work well.
# class IdeaLocAdder:
    # def __init__(self, input_file, output_file):
    #     self.input_file = input_file
    #     self.output_file = output_file

    # def extract_idea_names(self):
    #     idea_names = []
    #     inside_ideas = False
    #     try:
    #         with open(self.input_file, 'r', encoding='utf-8') as file:
    #             for line_number, line in enumerate(file, start=1):
    #                 if 'ideas =' in line:
    #                     inside_ideas = True
    #                     logging.info(f"Found 'ideas =' line at line {line_number}")
    #                 elif inside_ideas:
    #                     if '}' in line:
    #                         inside_ideas = False
    #                         logging.info(f"Closing 'ideas =' block at line {line_number}")
    #                     else:
    #                         idea_name_match = re.match(r'\s*([^\s={]+)\s*=', line)
    #                         if idea_name_match and not line.strip().startswith('#'):
    #                             idea_name = idea_name_match.group(1)
    #                             idea_names.append(idea_name)
    #                             logging.info(f"Found idea '{idea_name}' at line {line_number}")

    #     except FileNotFoundError:
    #         logging.error(f"File not found: {self.input_file}")
    #     return idea_names

    # def update_output_file(self):
    #     idea_names = self.extract_idea_names()

    #     try:
    #         with open(self.output_file, 'a', encoding='utf-8-sig') as file:
    #             with open(self.output_file, 'r', encoding='utf-8') as output_file_reader:
    #                 content = output_file_reader.read()

    #                 for idea_name in idea_names:
    #                     name_entry = f'{idea_name}: ""\n'
    #                     desc_entry = f'{idea_name}_desc: ""\n'

    #                     if idea_name not in content:
    #                         file.write(name_entry)
    #                     if f'{idea_name}_desc' not in content:
    #                         file.write(desc_entry)

    #     except FileNotFoundError:
    #         logging.error(f"File not found: {self.output_file}")

    # def process_files(self):
    #     self.update_output_file()
    #     logging.info("Idea file successfully updated.")

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Given a file, it adds missing localisation entries to a specified localisation file. Note: lines starting with "#" are IGNORED.')
    parser.add_argument('input_file', help='Path to the input file.')
    parser.add_argument('output_file', help='Path to the output file.')

    args = parser.parse_args()

    
    try:
        args.input_file = Path(args.input_file)
        args.output_file = Path(args.output_file)
        
        if not args.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")
        if not args.output_file.exists():
            raise FileNotFoundError(f"Output file not found: {args.output_file}")
        if not args.input_file.is_file() or args.input_file.suffix.lower() != '.txt':
            raise ValueError("Input should be a .txt file.")
        if not args.output_file.is_file() or args.output_file.suffix.lower() != '.yml':
            raise ValueError("Output should be a .yml file.")
        if 'l_english:' not in args.output_file.read_text(encoding='utf-8'):
            logging.warning("Output file doesn't contain 'l_english:'.")
        
        print(f"Input File: {args.input_file}")
        print(f"Output File: {args.output_file}")
        
        with args.input_file.open('r', encoding='utf-8') as file:
            if any('focus_tree' in line for line in file):
                print("Running FocusLocAdder")
                focus_adder = FocusLocAdder(args.input_file, args.output_file)
                focus_adder.process_files()
                logging.info("Focus tree file successfully updated!")
            else:
                logging.error("Unsupported fiel type. Please provide a valid national focus file")
    except Exception as e:
        logging.error(f"An error occured: {e}")

    # elif 'common/ideas' in input_path:
    #     print("Running IdeaLocAdder...")
    #     idea_adder = IdeaLocAdder(input_path, output_path)
    #     idea_adder.process_files()
    #     logging.info("Idea file successfully updated.")

if __name__ == "__main__":
    main()