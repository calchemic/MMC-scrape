#!/usr/bin/env python3

import os
import re
import json
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse
from firecrawl import FirecrawlApp

class CourseContentScraper:
    def __init__(self, api_key):
        """Initialize the scraper with Firecrawl API key"""
        self.app = FirecrawlApp(api_key=api_key)
        
    def extract_folder_name(self, url):
        """Extract folder name from URL (last element before imsmanifest.xml)"""
        path_parts = url.rstrip('/').split('/')
        for i, part in enumerate(path_parts):
            if part == 'imsmanifest.xml':
                if i > 0:
                    return path_parts[i-1]
        
        if len(path_parts) >= 2:
            return path_parts[-2]
        return "course_content"
    
    def get_base_url(self, url):
        """Get base URL without the filename"""
        return url.rsplit('/', 1)[0] + '/'
    
    def create_folder_structure(self, folder_name):
        """Create the main folder and subfolders"""
        main_folder = Path(folder_name)
        json_folder = main_folder / "JSON"
        images_folder = main_folder / "extracted_images"
        
        main_folder.mkdir(exist_ok=True)
        json_folder.mkdir(exist_ok=True)
        images_folder.mkdir(exist_ok=True)
        
        return main_folder, json_folder, images_folder
    
    def scrape_and_save(self, url, output_path, description="page"):
        """Scrape a URL and save to file"""
        try:
            print(f"Scraping {description}: {url}")
            result = self.app.scrape_url(url, formats=['markdown', 'html'])
            
            if hasattr(result, 'success') and result.success:
                # Save both markdown and HTML if available
                if hasattr(result, 'markdown') and result.markdown:
                    md_path = output_path.with_suffix('.md')
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(result.markdown)
                    print(f"✅ Saved markdown to: {md_path}")
                
                if hasattr(result, 'html') and result.html:
                    html_path = output_path.with_suffix('.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(result.html)
                    print(f"✅ Saved HTML to: {html_path}")
                
                # Save metadata
                if hasattr(result, 'metadata') and result.metadata:
                    metadata_path = output_path.with_suffix('.metadata.json')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        metadata_dict = result.metadata if isinstance(result.metadata, dict) else result.metadata.__dict__
                        json.dump(metadata_dict, f, indent=2)
                
                return result
            else:
                print(f"❌ Failed to scrape {url}")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            return None
    
    def find_json_files_from_manifest(self, xml_content):
        """Find JSON file references from the scraped manifest content"""
        json_files = []
        
        # Look in both markdown and HTML content
        text_content = ""
        if hasattr(xml_content, 'markdown') and xml_content.markdown:
            text_content += xml_content.markdown
        if hasattr(xml_content, 'html') and xml_content.html:
            text_content += xml_content.html
        
        # Find JSON file references using regex - look for dr/img*.json pattern
        json_pattern = r'dr/img\w*\.json'
        matches = re.findall(json_pattern, text_content, re.IGNORECASE)
        
        # Remove duplicates and sort
        json_files = sorted(list(set(matches)))
        
        print(f"📋 Found {len(json_files)} JSON files in manifest: {json_files}")
        return json_files
    
    def get_fallback_json_files(self, max_files=200):
        """Fallback method: try common JSON file patterns up to max_files"""
        json_files = []
        
        # Add dr/img1.json through dr/img{max_files}.json
        for i in range(1, max_files + 1):
            json_files.append(f"dr/img{i}.json")
        
        # Add common metadata files
        json_files.extend(["dr/imgmd.json", "dr/metadata.json"])
        
        print(f"📋 Using fallback: trying up to {max_files} img files + metadata files")
        return json_files
    
    def run_extract_images_all(self, json_folder_path):
        """Run extract_images_all.py on the JSON folder to extract all images"""
        try:
            if os.path.exists('extract_images_all.py'):
                print(f"Running extract_images_all.py on JSON folder: {json_folder_path}")
                result = subprocess.run([
                    'python3', 'extract_images_all.py', 
                    str(json_folder_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    if "Total images extracted:" in result.stdout:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "🖼️  Total images extracted:" in line:
                                print(f"✅ {line.strip()}")
                                break
                    else:
                        print(f"✅ Image extraction completed for JSON folder")
                    
                    if "EXTRACTION COMPLETE!" in result.stdout:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "📊 Successfully processed:" in line or "🖼️  Total images extracted:" in line or "📁 Images saved to:" in line:
                                print(f"✅ {line.strip()}")
                else:
                    print(f"❌ Error running extract_images_all.py: {result.stderr}")
            else:
                print("⚠️  extract_images_all.py not found in current directory - skipping image extraction")
        except Exception as e:
            print(f"❌ Error running extract_images_all.py: {str(e)}")
    
    def process_course_url(self, xml_url):
        """Main method to process a course URL"""
        print(f"🎯 Processing course URL: {xml_url}")
        
        # Extract folder name and base URL
        folder_name = self.extract_folder_name(xml_url)
        base_url = self.get_base_url(xml_url)
        
        print(f"📁 Folder name: {folder_name}")
        print(f"🌐 Base URL: {base_url}")
        
        # Create folder structure
        main_folder, json_folder, images_folder = self.create_folder_structure(folder_name)
        
        print(f"\n{'='*60}")
        print("📄 STEP 1: SCRAPING XML MANIFEST")
        print(f"{'='*60}")
        
        # Step 1: Scrape the XML file
        xml_content = self.scrape_and_save(
            xml_url, 
            main_folder / "imsmanifest", 
            "XML manifest"
        )
        
        if not xml_content:
            print("❌ Failed to scrape XML file. Stopping.")
            return
        
        print(f"\n{'='*60}")
        print("📄 STEP 2: DISCOVERING AND SCRAPING JSON FILES")
        print(f"{'='*60}")
        
        # Step 2: Try to discover JSON files from manifest first
        json_files = self.find_json_files_from_manifest(xml_content)
        
        # If no files found in manifest, use fallback method
        if not json_files:
            print("⚠️  No JSON files found in manifest, using fallback method...")
            json_files = self.get_fallback_json_files(max_files=50)  # Try up to 50 files by default
        
        successful_json_files = 0
        total_json_files = len(json_files)
        failed_files = []
        
        for i, json_file in enumerate(json_files, 1):
            print(f"📄 Processing {i}/{total_json_files}: {json_file}")
            # Create full URL for JSON file
            json_url = urljoin(base_url, json_file)
            
            # Create safe filename
            safe_filename = json_file.replace('/', '_').replace('\\', '_')
            json_output_path = json_folder / safe_filename
            
            # Scrape JSON file
            json_content = self.scrape_and_save(
                json_url, 
                json_output_path, 
                f"JSON file ({json_file})"
            )
            
            # Save the JSON content properly
            if json_content:
                successful_json_files += 1
                markdown_content = None
                if hasattr(json_content, 'markdown') and json_content.markdown:
                    markdown_content = json_content.markdown
                elif isinstance(json_content, dict) and 'markdown' in json_content:
                    markdown_content = json_content['markdown']
                
                if markdown_content:
                    json_file_path = json_output_path.with_suffix('.json')
                    try:
                        json_data = json.loads(markdown_content)
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, indent=2)
                    except json.JSONDecodeError:
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
            else:
                failed_files.append(json_file)
        
        print(f"\n✅ Successfully scraped {successful_json_files}/{total_json_files} JSON files")
        if failed_files:
            print(f"❌ Failed files: {failed_files[:5]}{'...' if len(failed_files) > 5 else ''}")  # Show first 5 failed files
        
        print(f"\n{'='*60}")
        print("🖼️  STEP 3: EXTRACTING IMAGES FROM ALL JSON FILES")
        print(f"{'='*60}")
        # Step 3: Extract images from all JSON files at once
        self.run_extract_images_all(json_folder)
        
        print(f"\n{'='*60}")
        print("📄 STEP 4: SCRAPING CPM.JS")
        print(f"{'='*60}")
        
        # Step 4: Scrape CPM.js
        cpm_url = urljoin(base_url, "assets/js/CPM.js")
        cpm_result = self.scrape_and_save(
            cpm_url, 
            main_folder / "CPM.js", 
            "CPM.js file"
        )
        
        if cpm_result:
            print("✅ CPM.js successfully scraped")
        else:
            print("❌ Failed to scrape CPM.js")
        
        print(f"\n{'='*60}")
        print("📄 STEP 5: SCRAPING PROJECT.TXT")
        print(f"{'='*60}")
        
        # Step 5: Scrape project.txt
        project_url = urljoin(base_url, "project.txt")
        project_result = self.scrape_and_save(
            project_url, 
            main_folder / "project.txt", 
            "project.txt file"
        )
        
        if project_result:
            print("✅ project.txt successfully scraped")
        else:
            print("❌ Failed to scrape project.txt")
        
        print(f"\n{'='*60}")
        print("🎉 SCRAPING COMPLETED!")
        print(f"{'='*60}")
        print(f"📁 Check the '{folder_name}' folder for results:")
        print(f"   ├── imsmanifest.md/html")
        print(f"   ├── CPM.js.md/html")
        print(f"   ├── project.txt.md/html")
        print(f"   ├── JSON/ ({successful_json_files} files)")
        print(f"   └── extracted_images/ (extracted images)")


def main():
    # Configuration
    API_KEY = "fc-8f39409fee9545d98aa3faa2e08357e9"
    
    # Test URL 
    xml_url = "https://www.michaelmanagement.com/files/training/s4-sap102/s4-sap102_03/imsmanifest.xml"
    
    print("🎯 FIRECRAWL COURSE CONTENT SCRAPER")
    print(f"📁 URL: {xml_url}")
    print("="*60)
    
    # Create scraper instance
    scraper = CourseContentScraper(API_KEY)
    
    # Process the URL
    scraper.process_course_url(xml_url)

if __name__ == "__main__":
    main() 