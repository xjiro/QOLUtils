# QOLUtils

A collection of quality-of-life utilities for common tasks.

## autocrop

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


## clipqr

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


## filelist

Cross-platform utility for comparing directory contents. Makes a script to zip differences between two directories for combining. 

**Usage:**
```bash
python filelist.py
```

**Features:**
1. **Dump Directory to JSON** - Scans a directory and makes a metadata file to compare.

2. **Compare File Lists** - Compare two generated metadata files. Shows:
   - Files present in both lists
   - Files unique to A
   - Files unique to B
   - Total counts and sizes for each category

   Also generates a a script (`zip_different_files.py`) to create a zip in either directory of only the mutually exclusive contents.


## passwdhash

Generate password hashes in multiple formats for manual use.

**Usage:**
```bash
python passwdhash.py
```

**What it does:**
- Prompts for username and password
- Generates three different hash formats:
  - **bcrypt** - Modern password hashing standard (default parameters)
  - **.htpasswd** - bcrypt hash formatted for Apache .htpasswd files (12 rounds)
  - **passlib pbkdf2_sha256** - PBKDF2-SHA256 hash for Python applications
  - **SHA3-256** - hashlib's SHA-3 256-bit hash in hex
- Generates random keys for:
  - **Fernet**


## Installation

```bash
# Clone the repository
git clone git@github.com:xjiro/QOLUtils.git
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