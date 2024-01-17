import os

#############################
###
### HoI 4 Auto Goal Adder, created by Thanasis Lanaras
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
###
#############################################################

### usage: autogoaler.py
###
### The script will request a filename, and it will check if it exists on gfx/interface/goals folder
### If it does exist, it will create a goals.gfx entry using the filename
### then ask for another one
### if you want to exit the script instead, write exit.
### The script is also specifically written to support FX files, 
### though it is very easy to change the paths if you want to.

#############################################################

while True:
    current_directory = os.getcwd()
    goal_directory = os.path.join(current_directory, "gfx/interface/goals")

    filename = input("Enter the filename (or 'exit' to quit): ")
    sprite_id = os.path.splitext(filename)[0]  # Remove the file extension

    if filename.lower() == 'exit':
        break

    matching_files = [f for f in os.listdir(goal_directory) if f == filename]

    if not matching_files:
        print(f"File '{filename}' not found in the 'gfx/interface/goals' directory.")
        continue

    interface_directory = os.path.join(current_directory, "interface")
    fx_goals_filepath = os.path.join(interface_directory, "FX_goals.gfx")

    with open(fx_goals_filepath, 'a', encoding="utf-8") as fx_goals_file:
        # Step 6: Find the last closing bracket of the spriteTypes block
        last_bracket = None
        with open(fx_goals_filepath, 'r', encoding="utf-8") as fx_goals_read:
            lines = fx_goals_read.readlines()
            for index, line in enumerate(reversed(lines)):
                if "}" in line:
                    last_bracket = len(lines) - index - 1
                    break

        if last_bracket is not None:

            new_filename = os.path.join("gfx/interface/goals", filename).replace("\\", "/")
            new_sprite_type = f'\n\tspriteType = {{\n\t\tname = "GFX_goal_{sprite_id}"\n\t\ttextureFile = "{new_filename}"\n\t}}'

            lines.insert(last_bracket, new_sprite_type + "\n")

            with open(fx_goals_filepath, 'w', encoding="utf-8") as fx_goals_rewrite:
                fx_goals_rewrite.writelines(lines)

            print(f"New SpriteType entry added for '{filename}'")
        else:
            print("No closing bracket found for spriteTypes block in 'FX_goals.gfx'")

print("Exiting the script.")
