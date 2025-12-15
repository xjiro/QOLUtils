# QOLUtils

A collection of quality-of-life utilities for common media manipulation tasks.

## Tools

### autocrop

Automatically trims and crops letterboxing or empty space from images and videos.

**Usage:**
```bash
# Crop an image, output filename will be generated
autocrop.py image.png

# Crop an image with custom output name
autocrop.py image.png -o cropped_image.png

# Replace the source file with the cropped version
autocrop.py image.png -r

# Also works with videos
autocrop.py video.mp4
```

**What it does:**
- **For images:** Detects the most common edge color and crops it away
- **For videos:** Uses ffmpeg's cropdetect filter to find and remove letterboxing/pillarboxing


### clipqr

Bidirectional QR code tool:
- If your clipboard has text, put a QR code image of it in your clipboard.
- If your clipboard has an image, try to read it as a barcode/QR code and put the text in your clipboard.


**Usage:**
```bash
clipqr.py
```

**What it does:**
- **Text in clipboard:** Generates a QR code image and puts it in the clipboard
- **Image in clipboard:** Reads any QR codes or barcodes in the image and puts the decoded text in the clipboard


## Installation

```bash
# Clone the repository
git clone <repository-url>
cd QOLUtils

# Install Python dependencies
pip install -Ur requirements.txt
```

Link or put the `.py` files in your system PATH

For video cropping, install ffmpeg:
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## License

MIT. See [LICENSE](LICENSE) file for details.