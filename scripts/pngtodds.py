#!/usr/bin/env python3
"""
PNG to DDS Converter (DX11+ B8G8R8A8 Linear, Uncompressed)
Requires: pip install pillow
"""

import argparse
import sys
from pathlib import Path
from PIL import Image


def convert_png_to_dds(input_path: Path, output_path: Path = None) -> Path:
    """Convert a PNG file to DX11+ B8G8R8A8 Linear DDS format."""
    if output_path is None:
        output_path = input_path.with_suffix('.dds')
    
    img = Image.open(input_path).convert('RGBA')
    
    img.save(output_path, 'DDS', dxgi_format='B8G8R8A8_UNORM')
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Convert PNG to DX11+ B8G8R8A8 DDS')
    parser.add_argument('input', type=Path, help='Input PNG file')
    parser.add_argument('-o', '--output', type=Path, default=None, help='Output DDS file')
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        output = convert_png_to_dds(args.input, args.output)
        print(f"Converted: {args.input} -> {output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
