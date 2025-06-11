#!/usr/bin/env python3

from firecrawl_scraper import CourseContentScraper

def main():
    # Your Firecrawl API key
    API_KEY = "fc-8f39409fee9545d98aa3faa2e08357e9"
    
    # Example URL - replace with your actual URL
    xml_url = "https://www.michaelmanagement.com/files/training/s4-sap102/s4-sap102_03/imsmanifest.xml"
    
    # Create scraper instance
    scraper = CourseContentScraper(API_KEY)
    
    # Process the URL
    scraper.process_course_url(xml_url)

if __name__ == "__main__":
    main() 