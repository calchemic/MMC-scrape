#!/usr/bin/env python3

from firecrawl_scraper import CourseContentScraper

def test_js_fix():
    """Test the JavaScript file scraping fix"""
    # Configuration
    API_KEY = "fc-ba99fd9162ef43d38402cf2b903ca6cd"
    
    # Test URL
    test_url = "https://www.michaelmanagement.com/files/training/PS101/ps101_01/imsmanifest.xml"
    
    print("="*60)
    print("🧪 TESTING JAVASCRIPT FILE SCRAPING FIX")
    print("="*60)
    print(f"Test URL: {test_url}")
    print()
    
    try:
        # Create scraper and process
        scraper = CourseContentScraper(API_KEY)
        scraper.process_course_url(test_url)
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETED!")
        print("="*60)
        print("🔍 To verify the fix worked:")
        print("1. Check the 'ps101_01' folder")
        print("2. Look for CPM.js file (should contain raw JavaScript code)")
        print("3. Look for 'Downloading raw file' messages in the output above")
        print("4. Verify CPM.js contains actual JS functions (not markdown)")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_js_fix() 