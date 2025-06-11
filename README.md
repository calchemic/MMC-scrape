# 🚀 MMC Course Scraper

A powerful, parallel web scraping tool designed to extract and process course content from Michael Management Company (MMC) training materials. Features intelligent JavaScript formatting, automated image extraction, and high-performance parallel processing with multiple API keys.

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

### ⚡ **High-Performance Parallel Processing**
- **Multi-API Key Support**: Utilizes up to 68 different Firecrawl API keys simultaneously
- **Intelligent Load Balancing**: Distributes courses across workers to avoid rate limiting
- **Scalable Architecture**: Processes 1,536+ courses with ~68x speedup over sequential processing
- **Progress Tracking**: Real-time monitoring of worker performance and success rates

### 📊 **Comprehensive Analytics**
- **Detailed Reporting**: CSV export of all processing results with timing and error data
- **Performance Metrics**: Processing rates, success rates, and speedup calculations
- **Worker Performance**: Individual API key performance tracking

## 📁 Project Structure

```
MMC-scrape/
├── scripts/                    # Core scraping scripts
│   ├── firecrawl_scraper.py   # Main scraper class with JS formatting
│   ├── parallel_scraper_demo.py # Demo: 10 courses in parallel
│   ├── parallel_scraper_full.py # Full: All 1,536 courses
│   ├── extract_images_all.py  # Bulk image extraction
│   ├── extract_images_now.py  # Single folder image extraction
│   ├── fixed_scraper.py       # Legacy scraper (pre-JS fix)
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

#### 2. **Full Production Run (All 1,536 Courses)**
```bash
python scripts/parallel_scraper_full.py
```
- Processes all courses with 68 parallel workers
- Each worker handles ~23 courses sequentially
- Estimated completion: ~1.5 hours
- Generates comprehensive results CSV

#### 3. **Single Course Processing**
```bash
python scripts/firecrawl_scraper.py
```
- Interactive single course processing
- Manual URL input and testing
- Detailed output for debugging

## 📊 Performance Benchmarks

### **Demo Results (10 Courses)**
- **Total Time**: 113.4 seconds
- **Speedup**: 5.8x faster than sequential
- **Success Rate**: 100% (10/10 courses)
- **Images Extracted**: 2,257 total images
- **Processing Rate**: 5.3 courses/minute

### **Projected Full Run (1,536 Courses)**
- **Estimated Time**: ~1.5 hours parallel vs ~30 hours sequential
- **Expected Speedup**: ~68x (one worker per API key)
- **Estimated Images**: ~350,000+ images
- **Processing Rate**: ~17 courses/minute

## 🔧 Technical Architecture

### **Parallel Processing Design**
- **Worker Distribution**: Each of 68 API keys assigned ~23 courses
- **Load Balancing**: Round-robin assignment prevents rate limiting
- **Error Handling**: Individual course failures don't stop other workers
- **Progress Monitoring**: Real-time worker status and completion tracking

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
    └── ... (200-350 images per course)
```

### **Global Results**
- **scraping_results.csv**: Comprehensive processing log
- **Performance metrics**: Success rates, timing data, error analysis
- **Worker statistics**: Individual API key performance

## 🛠️ Configuration

### **API Keys Setup**
- Place Firecrawl API keys in `API keys.txt` (one per line)
- Currently configured for 68 keys
- Automatic round-robin distribution

### **Course Database**
- `MMC Lessons All Simulation Lessons.csv` contains all course metadata
- Fields: courseid, coursename, lessonID, lessonname, link
- 1,536 total courses across multiple training programs

## 🔍 Monitoring & Debugging

### **Real-time Progress**
- Worker status updates
- Individual course completion times
- Success/failure rates per worker
- API key performance tracking

### **Error Handling**
- Timeout management for slow responses
- Rate limit detection and handling
- Detailed error logging with truncated messages
- Graceful degradation on individual failures

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

### **v1.0 - Core Features**
- ✅ Basic Firecrawl integration
- ✅ JSON file discovery and processing
- ✅ Base64 image extraction
- ✅ Multi-format output (MD/HTML)

## 🚀 Future Enhancements

- **Resume Capability**: Restart failed/interrupted runs
- **Dynamic Scaling**: Adjust worker count based on API limits
- **Content Validation**: Verify extracted content completeness
- **Advanced Analytics**: Course content analysis and reporting
- **Cloud Deployment**: AWS/GCP parallel processing at scale

## 📞 Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.

---

**🎉 Ready to process 1,536 courses in parallel? Run `python scripts/parallel_scraper_full.py` and watch the magic happen!** 