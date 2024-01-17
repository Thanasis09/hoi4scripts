from PIL import Image
import os

#############################################################

### usage: ddsToPng.py
###
### The script does not use argparse or another utility to parse the files, and instead relies that you put the paths manually.
### This may be changed soon to support command-line arguments.
### The script uses pillow module, which may not be installed on your machine. To install, run 
### pip install pillow
###
### Using an input folder and an output folder, it converts all files on input folder to png from dds.
### Warning: It does not change the spriteType entries, you have to do that manually possibly using find all + replace.
### The script is meant for those that want to convert all their files to png from dds, as dds is a format that is really quirky
### and hoi4 does support png.

def convert_to_png(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for root, _, filenames in os.walk(input_folder):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext.lower() == '.dds':
                input_path = os.path.join(root, filename)
                output_path = os.path.join(output_folder, name + '.png' )

                try:
                    img = Image.open(input_path)
                    img.save(output_path)
                    print(f"Converted: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Error converting {input_path}: {e}")
                    
def main():
    input_folder = "gfx"
    output_folder = "gfx/converted/"
    convert_to_png(input_folder, output_folder)

if __name__ == "__main__":
    main()