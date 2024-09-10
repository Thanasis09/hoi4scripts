import os
from PIL import Image
import argparse
from typing import Tuple, List

#############################
###
### HoI 4 Auto-Framer, created by Thanasis Lanaras
### Written in Python 3.12.1
###
###    Copyright (C) 2024 Thanasis Lanaras.
###
### This program is free software: you can redistribute it and/or modify
### it under the terms of the GNU Affero General Public License as published
### by the Free Software Foundation, version 3 of the License.
### See <https://www.gnu.org/licenses/>. for the AGPL-3.0 license.

### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU Affero General Public License for more details.


def generate_shades(start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], num_shades: int) -> List[Tuple[int, int, int]]:
    """Generate a list of shades between start_color and end_color."""
    return [
        tuple(
            int(start_color[j] + (end_color[j] - start_color[j]) * (i / (num_shades - 1)))
            for j in range(3)
        )
        for i in range(num_shades)
    ]

def adjust_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Adjust the brightness of a color by a given factor."""
    return tuple(max(min(int(c * factor), 255), 0) for c in color)

def replace_color(image: Image.Image, target_color: Tuple[int, int, int], replacement_color: Tuple[int, int, int]) -> Image.Image:
    """Replace the target color in the image and return the modified image."""
    img = image.convert('RGBA')
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            current_color = pixels[x, y]
            if current_color[:3] == target_color and current_color[3] != 0:
                pixels[x, y] = (*replacement_color, current_color[3])

    return img

def combine_images(images: List[Image.Image], output_path: str) -> None:
    """Combine multiple images into a single image, side by side."""
    
    if not images:
        print("No images to combine.")
        return
    
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    combined_img = Image.new('RGBA', (total_width, max_height))
    
    x_offset = 0
    for img in images:
        combined_img.paste(img, (x_offset, 0))
        x_offset += img.width
    
    combined_img.save(output_path)
    print(f"Combined image saved to {output_path}")

def process_images(input_folder: str, output_folder: str, target_color: Tuple[int, int, int], start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], num_shades: int) -> None:
    """Process all images in the input folder and save combined images to the output folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    try:
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    except FileNotFoundError:
        print(f"Input folder '{input_folder}' not found.")
        return
    
    if not image_files:
        print("No image files found in the input folder.")
        return
    
    start_gradient = generate_shades(adjust_color(start_color, 0.5), adjust_color(start_color, 1.5), num_shades)
    end_gradient = generate_shades(adjust_color(end_color, 1.5), adjust_color(end_color, 0.5), num_shades)
    
    for image_file in image_files:
        image_path = os.path.join(input_folder, image_file)
        try:
            original_image = Image.open(image_path)
        except IOError:
            print(f"Failed to open image {image_file}. Skipping.")
            continue
        
        images = [replace_color(original_image, target_color, color) for color in start_gradient + end_gradient]
        
        combined_output_path = os.path.join(output_folder, f"combined_{image_file}")
        combine_images(images, combined_output_path)

def main() -> None:
    parser = argparse.ArgumentParser(description='Process images by replacing target colors with varying shades and combine them.')
    parser.add_argument('-i', '--input_folder', type=str, default='./', help='Input folder containing the images to process')
    parser.add_argument('-o', '--output_folder', type=str, default='./out', help='Output folder to save the combined images')
    parser.add_argument('-t', '--target_color', type=int, nargs=3, default=[33, 64, 31], help='Target color to replace in the images (R G B)')
    parser.add_argument('-sc', '--start_color', type=int, nargs=3, required=True, help='Starting color for gradient (R G B)')
    parser.add_argument('-ec', '--end_color', type=int, nargs=3, required=True, help='Ending color for gradient (R G B)')
    parser.add_argument('-n', '--num_shades', type=int, default=10, help='Number of shades for red and green colors')
    
    args = parser.parse_args()
    target_color = tuple(args.target_color)
    start_color = tuple(args.start_color)
    end_color = tuple(args.end_color)
    
    if args.num_shades < 2:
        parser.error("num_shades must be greater than 1.")
        return
    
    process_images(args.input_folder, args.output_folder, target_color, start_color, end_color, args.num_shades)

if __name__ == "__main__":
    main()
