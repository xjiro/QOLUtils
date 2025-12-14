import subprocess
import re
import os
import argparse
import mimetypes
import tempfile
from PIL import Image, ImageChops

def get_crop_dimensions(input_file):
    """
    Uses ffmpeg's cropdetect filter to find optimal crop dimensions.
    """
    print(f"Analyzing {input_file} for crop dimensions...")
    # Run ffmpeg with cropdetect filter on a small sample of the video
    command = [
        'ffmpeg', '-i', input_file, '-ss', '00:00:00', '-t', '10',  # Analyze first 10 seconds
        '-vf', 'cropdetect=limit=24:round=16:reset=0', '-f', 'null', '-'
    ]
    
    # Run the command and capture stderr output (where ffmpeg logs filter info)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Regex to find the last reported crop dimensions in the stderr output
    # Example output: "[Parsed_cropdetect_0 @ 0x...] crop=1920:816:0:132"
    crop_params_match = re.findall(r"crop=\d+:\d+:\d+:\d+", stderr)
    
    if crop_params_match:
        last_crop_params = crop_params_match[-1]
        print(f"Detected crop parameters: {last_crop_params}")
        return last_crop_params
    else:
        print("Could not automatically detect crop parameters.")
        return None

def apply_crop(input_file, output_file, crop_params):
    """
    Applies the detected crop dimensions to the input video and saves it.
    """
    if not crop_params:
        return

    print(f"Applying crop {crop_params} to {input_file}...")
    # Run ffmpeg to apply the crop filter and re-encode the video
    command = [
        'ffmpeg', '-i', input_file,
        '-vf', crop_params,
        '-c:a', 'copy',  # Copy the audio stream to avoid re-encoding it
        output_file
    ]

    subprocess.run(command, check=True)
    print(f"Successfully cropped and saved to {output_file}")

def is_image(file_path):
    """
    Check if the file is an image based on mimetype.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('image/')

def crop_image_by_common_side(input_file, output_file):
    """
    Crops an image by sampling the middle pixel of each edge and cropping away
    the color that appears on the majority of the edges.
    """
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_cropped{ext}"
    
    print(f"Analyzing {input_file} for edge colors...")
    img = Image.open(input_file)
    width, height = img.size
    
    # Sample middle pixel from each edge
    top_color = img.getpixel((width // 2, 0))
    bottom_color = img.getpixel((width // 2, height - 1))
    left_color = img.getpixel((0, height // 2))
    right_color = img.getpixel((width - 1, height // 2))
    
    # Count occurrences of each color
    edge_colors = [top_color, bottom_color, left_color, right_color]
    color_count = {}
    for color in edge_colors:
        color_count[color] = color_count.get(color, 0) + 1
    
    # Find the color that appears most frequently
    crop_color = max(color_count, key=color_count.get)
    
    print(f"Edge colors - Top: {top_color}, Bottom: {bottom_color}, Left: {left_color}, Right: {right_color}")
    print(f"Cropping color: {crop_color} (appears on {color_count[crop_color]} edges)")
    
    # Create a background image filled with the crop color
    bg = Image.new(img.mode, img.size, crop_color)
    
    # Find the difference between the image and the background
    diff = ImageChops.difference(img, bg)
    
    # Convert to RGB if needed for getbbox
    if diff.mode != 'RGB':
        diff = diff.convert('RGB')
    
    # Get the bounding box of non-crop-color pixels
    bbox = diff.getbbox()
    
    if bbox:
        cropped = img.crop(bbox)
        # Save with maximum quality - preserve original format
        if output_file.lower().endswith(('.jpg', '.jpeg')):
            cropped.save(output_file, quality=100, subsampling=0)
        elif output_file.lower().endswith('.png'):
            cropped.save(output_file, compress_level=0)
        else:
            cropped.save(output_file)
        print(f"Successfully cropped and saved to {output_file}")
        print(f"Original size: {width}x{height}, Cropped size: {cropped.size[0]}x{cropped.size[1]}")
    else:
        print("No cropping needed - entire image is the crop color")
        # Save with maximum quality
        if output_file.lower().endswith(('.jpg', '.jpeg')):
            img.save(output_file, quality=100, subsampling=0)
        elif output_file.lower().endswith('.png'):
            img.save(output_file, compress_level=0)
        else:
            img.save(output_file)

def main():
    parser = argparse.ArgumentParser(
        description='Auto-crop images (by top-left pixel color) or videos (using ffmpeg cropdetect)'
    )
    parser.add_argument('input', help='Input image or video file')
    parser.add_argument('-o', '--output', help='Output file (optional, will auto-generate if not provided)')
    parser.add_argument('-r', '--replace', action='store_true', help='Replace the source file (overrides -o)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        return
    
    # Determine output file
    if args.replace:
        # Create temp file for output
        base, ext = os.path.splitext(args.input)
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(temp_fd)
        output_file = temp_path
    elif args.output:
        output_file = args.output
    else:
        output_file = None
    
    if is_image(args.input):
        # Process as image
        crop_image_by_common_side(args.input, output_file)
    else:
        # Process as video
        if output_file is None:
            base, ext = os.path.splitext(args.input)
            output_file = f"{base}_cropped{ext}"
        
        params = get_crop_dimensions(args.input)
        if params:
            apply_crop(args.input, output_file, params)
    
    # Replace source file if -r flag was used
    if args.replace:
        os.remove(args.input)
        os.rename(output_file, args.input)
        print(f"Replaced {args.input} with cropped version")

if __name__ == '__main__':
    main()
