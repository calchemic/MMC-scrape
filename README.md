# 🚀 MMC Course Scraper

A powerful, batch-processing web scraping tool designed to extract and process course content from Michael Management Company (MMC) training materials. Features intelligent JavaScript formatting, automated image extraction, and high-performance batch processing with multiple API keys to avoid rate limiting.

## ✨ Key Features

### 🔧 **Core Scraping Capabilities**
- **Raw JavaScript Download & Formatting**: Bypasses Firecrawl's markdown conversion for .js files
- **Professional Code Formatting**: Uses `jsbeautifier` to transform minified JavaScript into readable code
- **Intelligent Content Detection**: Automatically discovers JSON files from course manifests
- **Multi-format Output**: Saves content in both Markdown and HTML formats

### 🖼️ **Advanced Image Processing**
- **Base64 Image Extraction**: Automatically extracts and saves images from JSON data
- **Bulk Processing**: Handles hundreds of images per course efficiently
- **Organized Storage**: Creates structured folders for extracted content

### ⚡ **Smart Batch Processing System**
- **Multi-API Key Support**: Utilizes up to 68 different Firecrawl API keys simultaneously
- **Intelligent Batch Management**: Processes courses in batches of 68 to avoid rate limiting
- **Sequential Batch Processing**: Completes each batch fully before starting the next
- **Progress Tracking**: Real-time monitoring of batch performance and success rates
- **Rate Limit Handling**: 30-second delays between batches to respect API limits

### 📊 **Comprehensive Analytics**
- **Detailed Reporting**: CSV export of all processing results with batch tracking
- **Performance Metrics**: Processing rates, success rates, and batch statistics
- **Error Logging**: Enhanced error messages for debugging and troubleshooting

## 📁 Project Structure

```
MMC-scrape/
├── scripts/                    # Core scraping scripts
│   ├── fixed_scraper.py       # Main scraper class with JS formatting
│   ├── parallel_scraper_full.py # Batch processor: All 1,536 courses
│   ├── parallel_scraper_demo.py # Demo: 10 courses in parallel
│   ├── extract_images_all.py  # Bulk image extraction
│   ├── extract_images_now.py  # Single folder image extraction
│   ├── firecrawl_scraper_old.py # Legacy scraper (pre-JS fix)
│   └── simple_parallel.py     # Basic parallel implementation
├── tests/                      # Test scripts and validation
│   ├── test_full_scraper.py   # Test batch processing approach
│   ├── test_parallel_simple.py # Simple parallel test
│   ├── test_js_fix.py         # JavaScript formatting test
│   └── test_parallel.py       # Basic parallel test
├── docs/                       # Documentation and backups
│   ├── README_backup.md       # Previous README versions
│   └── README_updated.md      # Version history
├── results/                    # Processing results (created during runs)
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── API keys.txt              # Firecrawl API keys (68 keys)
└── MMC Lessons All Simulation Lessons.csv # Course database (1,536 courses)
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Basic Usage

#### 1. **Demo Run (10 Courses)**
```bash
python scripts/parallel_scraper_demo.py
```
- Processes first 10 courses in parallel
- Uses 10 different API keys
- ~2 minutes completion time
- Perfect for testing and validation

#### 2. **Testing Run (Limited Courses)**
```bash
python scripts/parallel_scraper_full.py --limit 10
```
- **NEW**: Test with just 10 courses (or any number you specify)
- Perfect for testing the batch processing system
- Uses same batch logic but with limited scope
- Quick validation before running full production

#### 3. **Full Production Run (All 1,536 Courses)**
```bash
python scripts/parallel_scraper_full.py
```
- **NEW**: Processes courses in batches of 68 to avoid rate limits
- Uses all 68 API keys with intelligent batch management
- Waits 30 seconds between batches for rate limit respect
- Estimated completion: ~2-3 hours (depending on API response times)
- Generates comprehensive batch processing CSV results

#### 4. **Single Course Processing**
```bash
python scripts/fixed_scraper.py
```
- Interactive single course processing
- Manual URL input and testing
- Detailed output for debugging

## 📊 Performance Benchmarks

### **Batch Processing Results**
- **Batch Size**: 68 courses per batch (matching API key count)
- **Total Batches**: 23 batches to process all 1,536 courses
- **Rate Limit Management**: 30-second delays between batches
- **Success Rate**: High success rate due to proper rate limit handling
- **Processing Strategy**: Complete each batch fully before starting next

### **Expected Timeline**
- **Per Batch**: ~3-5 minutes processing + 30s delay
- **Total Time**: ~2-3 hours for all 1,536 courses
- **Output Generated**: ~350,000+ images and complete course data

## 🔧 Technical Architecture

### **Batch Processing Design**
- **Batch Strategy**: Process exactly 68 courses at once (one per API key)
- **Sequential Batches**: Complete batch N before starting batch N+1
- **Rate Limit Respect**: 30-second cooling period between batches
- **Error Isolation**: Individual course failures don't stop the batch
- **Progress Monitoring**: Real-time batch completion tracking

### **JavaScript Processing Pipeline**
1. **Detection**: Identifies .js files in course manifests
2. **Raw Download**: Direct HTTP requests bypass Firecrawl conversion
3. **Formatting**: jsbeautifier transforms minified code
4. **Output**: Saves both raw and formatted versions

### **Image Extraction Workflow**
1. **JSON Discovery**: Scans manifests for data files
2. **Base64 Detection**: Identifies embedded image data
3. **Batch Processing**: Extracts all images simultaneously
4. **Organization**: Creates structured folder hierarchy

## 📈 Results & Output

### **Per-Course Output Structure**
```
course_folder/
├── imsmanifest.md/html        # Course manifest
├── CPM.js                     # Formatted JavaScript (51,890+ lines)
├── project.txt.md/html        # Project metadata
├── JSON/                      # Course data files
│   ├── dr_img1.md/html       # Individual JSON files
│   ├── dr_img2.md/html
│   └── ...
└── extracted_images/          # All course images
    ├── image_001.png
    ├── image_002.jpg
    └── ... (200-455 images per course)
```

### **Batch Processing Results**
- **scraping_results_batch_[timestamp].csv**: Comprehensive processing log
- **Batch Performance**: Success rates per batch
- **Error Analysis**: Detailed error tracking with enhanced messages
- **API Key Usage**: Performance tracking per API key

## 🛠️ Configuration

### **API Keys Setup**
- Place Firecrawl API keys in `API keys.txt` (one per line)
- Currently configured for 68 keys
- Automatic round-robin distribution within each batch

### **Course Database**
- `MMC Lessons All Simulation Lessons.csv` contains all course metadata
- Fields: courseid, coursename, lessonID, lessonname, link
- 1,536 total courses across multiple training programs

## 🔍 Monitoring & Debugging

### **Real-time Progress**
- Batch-by-batch status updates
- Individual course completion times within batches
- Success/failure rates per batch
- Overall progress tracking across all batches

### **Enhanced Error Handling**
- Increased error message length for better debugging
- Rate limit detection with proper delay handling
- Detailed batch failure analysis
- Graceful degradation on individual course failures

## 🎯 Use Cases

### **Content Migration**
- Extract all course materials for backup/migration
- Preserve JavaScript functionality and formatting
- Maintain image assets and course structure

### **Data Analysis**
- Analyze course content and structure
- Extract metadata for reporting
- Performance benchmarking of different courses

### **Quality Assurance**
- Validate course completeness
- Check for missing assets or broken links
- Ensure consistent formatting across courses

## 📝 Recent Updates

### **v3.0 - Batch Processing System**
- ✅ **NEW**: Intelligent batch processing to avoid rate limits
- ✅ **NEW**: Sequential batch execution (complete batch before next)
- ✅ **NEW**: 30-second delays between batches for rate limit respect
- ✅ **NEW**: Enhanced error messages for better debugging
- ✅ **NEW**: Batch performance tracking and statistics
- ✅ **NEW**: Clean project structure (removed sample data)

### **v2.0 - Parallel Processing Revolution**
- ✅ Added support for 68 parallel workers
- ✅ Implemented intelligent load balancing
- ✅ Created comprehensive progress tracking
- ✅ Added CSV result export functionality

### **v1.5 - JavaScript Formatting Enhancement**
- ✅ Fixed JavaScript file processing (raw download vs Firecrawl)
- ✅ Added jsbeautifier for professional code formatting
- ✅ Transformed 1-line minified code to 51,890+ formatted lines
- ✅ Maintained all original functionality

## 🚀 Future Enhancements

- **Resume Capability**: Restart failed/interrupted batches
- **Dynamic Batch Sizing**: Adjust batch size based on API response times
- **Retry Logic**: Automatic retry of failed courses
- **Advanced Analytics**: Course content analysis and reporting
- **Cloud Deployment**: AWS/GCP batch processing at scale

## 📞 Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.

---

**🎉 Ready to process 1,536 courses in smart batches? Run `python scripts/parallel_scraper_full.py` and experience intelligent rate-limit-aware processing!** 