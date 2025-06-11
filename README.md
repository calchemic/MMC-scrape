# Firecrawl Course Content Scraper

A comprehensive Python tool that uses [Firecrawl](https://docs.firecrawl.dev/introduction) to automatically scrape and organize online course content from XML manifest files.

## 🎯 Features

- **🔍 Intelligent JSON Discovery**: Automatically detects JSON files from manifest or uses fallback method for courses with up to 200+ image files
- **📄 Complete Content Extraction**: Scrapes XML manifests, JSON data files, JavaScript files, and text files
- **✨ Professional JavaScript Formatting**: Automatically formats minified JavaScript files for readability using jsbeautifier
- **🖼️ Automated Image Extraction**: Extracts and decodes base64 images from JSON files with quality filtering
- **📁 Organized Output**: Creates structured folders with all content properly categorized
- **🚀 Scalable**: Handles courses with varying numbers of image files (1-200+)
- **⚡ Efficient**: Uses parallel processing and smart discovery methods

## 🆕 New JavaScript Formatting Feature

The scraper now automatically detects and formats JavaScript files for better readability:

- **Raw JavaScript Download**: `.js` files are downloaded directly (not converted to markdown)
- **Professional Formatting**: Minified JavaScript is automatically beautified with proper indentation
- **Preserved Functionality**: Formatted code remains fully functional
- **Readable Structure**: Easy to debug and analyze

**Before**: `if(!window.cp)window.cp=function(str){return document.getElementById(str)};`

**After**:
```javascript
if (!window.cp) window.cp = function(str) {
    return document.getElementById(str)
};
```

## 📦 Installation

1. **Install Python dependencies:**
```bash
pip install firecrawl-py requests jsbeautifier
```

2. **Set up your Firecrawl API key:**
   - The API key is already configured in the scripts
   - Get your key from [Firecrawl](https://docs.firecrawl.dev/introduction)

## 🚀 Quick Start

### Interactive Mode (Recommended)

```bash
python3 firecrawl_scraper.py
```

The script will prompt you to enter your course URL. Just paste your `imsmanifest.xml` URL when asked.

**Example:**
```
Enter the XML URL: https://example.com/path/to/course/imsmanifest.xml
```

### Direct Script Execution

1. **Open `firecrawl_scraper.py`**
2. **Find the main() function and update the URL:**
   ```python
   xml_url = "https://your-course-url.com/path/to/imsmanifest.xml"
   ```
3. **Run the script:**
   ```bash
   python3 firecrawl_scraper.py
   ```

## 🎯 Tested URLs

The scraper has been successfully tested on:

```
✅ https://www.michaelmanagement.com/files/training/PS101/ps101_01/imsmanifest.xml
✅ https://www.michaelmanagement.com/files/training/PS101/ps101_07/imsmanifest.xml
```

The script will automatically:
- Extract folder name from URL (e.g., `ps101_01`, `ps101_07`)
- Find all JSON files in the course
- Download and format CPM.js files
- Download project.txt files
- Extract all images

## 📁 Output Structure

For a course URL like `https://www.michaelmanagement.com/files/training/PS101/ps101_01/imsmanifest.xml`, the scraper creates:

```
ps101_01/
├── imsmanifest.md           # XML manifest (Markdown format)
├── imsmanifest.html         # XML manifest (HTML format)
├── imsmanifest.metadata.json # Scraping metadata
├── CPM.js                   # Formatted JavaScript file (51,890+ lines)
├── project.md               # project.txt (Markdown format)
├── project.html             # project.txt (HTML format)
├── JSON/                    # All JSON files discovered
│   ├── dr_img1.md           # Course image data (Markdown)
│   ├── dr_img1.html         # Course image data (HTML)
│   ├── dr_img2.md
│   ├── dr_img2.html
│   ├── ...
│   └── dr_imgmd.md          # Metadata files
└── extracted_images/        # Extracted and decoded images
    ├── image1.png
    ├── image2.png
    └── ... (341+ images for ps101_01, 186+ for ps101_07)
```

## 🛠️ Core Scripts

### Main Scripts
- **`firecrawl_scraper.py`** - Complete course scraper with JavaScript formatting (recommended)
- **`extract_images_all.py`** - Batch image extraction from JSON files
- **`test_js_fix.py`** - Test script for JavaScript formatting feature

## 🔧 JavaScript File Handling

The scraper automatically detects JavaScript files and:
1. Downloads them directly (bypassing Firecrawl conversion)
2. Applies professional formatting using `jsbeautifier`
3. Saves them with proper indentation and structure

**Configuration options** (in `_format_javascript` method):
- `indent_size`: 4 spaces (default)
- `max_preserve_newlines`: 2
- `wrap_line_length`: 120 characters
- `brace_style`: 'collapse'

## 📊 Success Metrics & Test Results

The scraper provides detailed progress reporting and has been tested on multiple courses:

### Test Results Summary:
- **ps101_01**: ✅ 8/9 JSON files, 341 images extracted, CPM.js formatted (51,890 lines)
- **ps101_07**: ✅ 4/6 JSON files, 186 images extracted, CPM.js formatted successfully

### Metrics Tracked:
- ✅ JSON files discovered and scraped
- 🖼️ Total images extracted with size validation
- ✨ JavaScript files formatted successfully
- 📁 Complete folder structure created
- ❌ Failed files logged for troubleshooting

## 🔍 How It Works

1. **📄 Manifest Analysis**: Scrapes the XML manifest file using Firecrawl
2. **🔍 JSON Discovery**: Uses intelligent pattern matching to find all JSON files
3. **📥 Content Extraction**: Downloads discovered files (JSON via Firecrawl, JS via direct HTTP)
4. **✨ JavaScript Formatting**: Automatically beautifies minified JavaScript files
5. **🖼️ Image Processing**: Extracts base64-encoded images with quality filtering
6. **📁 Organization**: Creates structured output folders

## 🐛 Troubleshooting

### Common Issues

**"No JSON files found"**
- The script will automatically fall back to trying standard patterns
- Increase the `max_files` parameter if you have more than 50 image files

**"Image extraction failed"**
- Check that `extract_images_all.py` is in the same directory
- Verify JSON files were properly downloaded

**"Firecrawl timeout"**
- Some files may timeout due to size or server issues
- The script continues processing other files automatically

**"JavaScript formatting failed"**
- The script falls back to basic formatting if jsbeautifier fails
- Original functionality is preserved even if formatting fails

### Dependencies

Make sure all required packages are installed:
```bash
pip install firecrawl-py requests jsbeautifier
```

## 🎉 Recent Updates

- ✨ **JavaScript Formatting**: Added professional JavaScript beautification
- 🔧 **Direct JS Download**: JavaScript files now downloaded as raw code (not markdown)
- 📊 **Enhanced Reporting**: Better progress tracking and success metrics
- 🧪 **Comprehensive Testing**: Verified on multiple course URLs (ps101_01, ps101_07)

## 📋 Requirements

The scraper requires these Python packages:
- `firecrawl-py` - For web scraping
- `requests` - For direct file downloads
- `jsbeautifier` - For JavaScript formatting 