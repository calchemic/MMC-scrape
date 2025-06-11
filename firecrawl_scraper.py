#!/usr/bin/env python3

import os
import re
import json
import subprocess
import requests
import jsbeautifier
from pathlib import Path
from urllib.parse import urljoin, urlparse
from firecrawl import FirecrawlApp

class CourseContentScraper:
    def __init__(self, api_key):
        """Initialize the scraper with Firecrawl API key"""
        self.app = FirecrawlApp(api_key=api_key)
        
    def extract_folder_name(self, url):
        """Extract folder name from URL (last element before imsmanifest.xml)"""
        # Remove the filename and get the last directory
        path_parts = url.rstrip('/').split('/')
        # Find the part before 'imsmanifest.xml'
        for i, part in enumerate(path_parts):
            if part == 'imsmanifest.xml':
                if i > 0:
                    return path_parts[i-1]
        
        # Fallback: get the second-to-last part of the path
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
        
        # Create directories
        main_folder.mkdir(exist_ok=True)
        json_folder.mkdir(exist_ok=True)
        images_folder.mkdir(exist_ok=True)
        
        return main_folder, json_folder, images_folder
    
    def scrape_and_save(self, url, output_path, description="page"):
        """Scrape a URL and save to file"""
        try:
            print(f"Scraping {description}: {url}")
            
            # Check if it's a JavaScript file that needs direct download
            if url.lower().endswith('.js'):
                return self._scrape_raw_file(url, output_path, description)
            
            # Use firecrawl for regular web pages
            result = self.app.scrape_url(url, formats=['markdown', 'html'])
            
            # Handle firecrawl-py response format
            if hasattr(result, 'success') and result.success:
                # Save both markdown and HTML if available
                if hasattr(result, 'markdown') and result.markdown:
                    md_path = output_path.with_suffix('.md')
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(result.markdown)
                    print(f"Saved markdown to: {md_path}")
                
                if hasattr(result, 'html') and result.html:
                    html_path = output_path.with_suffix('.html')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(result.html)
                    print(f"Saved HTML to: {html_path}")
                
                # Save metadata
                if hasattr(result, 'metadata') and result.metadata:
                    metadata_path = output_path.with_suffix('.metadata.json')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        # Convert metadata to dict if it's an object
                        metadata_dict = result.metadata if isinstance(result.metadata, dict) else result.metadata.__dict__
                        json.dump(metadata_dict, f, indent=2)
                
                return result
            else:
                print(f"Failed to scrape {url}: {result}")
                if hasattr(result, 'error') and result.error:
                    print(f"Error details: {result.error}")
                return None
                
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _scrape_raw_file(self, url, output_path, description):
        """Scrape raw files (JS, CSS, etc.) using direct HTTP request"""
        try:
            # Set proper headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            print(f"Downloading raw file: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raises an exception for bad status codes
            
            # Ensure proper encoding
            response.encoding = 'utf-8'
            
            content = response.text
            
            # Format JavaScript files for better readability
            if url.lower().endswith('.js'):
                content = self._format_javascript(content)
            
            # Save the content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Saved formatted {description} to: {output_path}")
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP error downloading {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None
    
    def _format_javascript(self, js_content):
        """Format minified JavaScript for better readability using jsbeautifier"""
        try:
            # Configure beautifier options
            options = jsbeautifier.default_options()
            options.indent_size = 4
            options.indent_char = ' '
            options.max_preserve_newlines = 2
            options.preserve_newlines = True
            options.keep_array_indentation = False
            options.break_chained_methods = True
            options.indent_scripts = 'normal'
            options.brace_style = 'collapse'
            options.space_before_conditional = True
            options.unescape_strings = False
            options.jslint_happy = False
            options.end_with_newline = True
            options.wrap_line_length = 120
            
            # Beautify the JavaScript
            formatted = jsbeautifier.beautify(js_content, options)
            
            print("✨ JavaScript formatted successfully with jsbeautifier")
            return formatted
            
        except Exception as e:
            print(f"Warning: Could not format JavaScript with jsbeautifier: {str(e)}")
            print("Falling back to basic formatting...")
            
            # Fallback to basic formatting
            try:
                # Simple line breaks after semicolons and braces
                formatted = js_content
                formatted = re.sub(r';(?=\s*[a-zA-Z_$])', ';\n', formatted)
                formatted = re.sub(r'\{(?=\s*[a-zA-Z_$])', '{\n', formatted)
                formatted = re.sub(r'\}(?=\s*[a-zA-Z_$])', '}\n', formatted)
                return formatted
            except:
                return js_content  # Return original if all formatting fails
    
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
                    # Count extracted images from output
                    if "Total images extracted:" in result.stdout:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "🖼️  Total images extracted:" in line:
                                print(f"✅ {line.strip()}")
                                break
                    else:
                        print(f"✅ Image extraction completed for JSON folder")
                    
                    # Print summary of the extraction
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
        print(f"Processing course URL: {xml_url}")
        
        # Extract folder name and base URL
        folder_name = self.extract_folder_name(xml_url)
        base_url = self.get_base_url(xml_url)
        
        print(f"Folder name: {folder_name}")
        print(f"Base URL: {base_url}")
        
        # Create folder structure
        main_folder, json_folder, images_folder = self.create_folder_structure(folder_name)
        
        # Step 1: Scrape the XML file
        xml_content = self.scrape_and_save(
            xml_url, 
            main_folder / "imsmanifest", 
            "XML manifest"
        )
        
        if not xml_content:
            print("Failed to scrape XML file. Stopping.")
            return
        
        # Step 2: Try to discover JSON files from manifest first
        json_files = self.find_json_files_from_manifest(xml_content)
        
        # If no files found in manifest, use fallback method
        if not json_files:
            print("⚠️  No JSON files found in manifest, using fallback method...")
            json_files = self.get_fallback_json_files(max_files=50)  # Try up to 50 files by default
        
        successful_json_files = 0
        total_json_files = len(json_files)
        
        for json_file in json_files:
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
                # Save the actual JSON content if available
                markdown_content = None
                if hasattr(json_content, 'markdown') and json_content.markdown:
                    markdown_content = json_content.markdown
                elif isinstance(json_content, dict) and 'markdown' in json_content:
                    markdown_content = json_content['markdown']
                
                if markdown_content:
                    json_file_path = json_output_path.with_suffix('.json')
                    try:
                        # Try to parse as JSON
                        json_data = json.loads(markdown_content)
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, indent=2)
                    except json.JSONDecodeError:
                        # If not valid JSON, save as text
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
        
        print(f"\n✅ Successfully scraped {successful_json_files}/{total_json_files} JSON files")
        
        # Step 2.5: Extract images from all JSON files at once
        print(f"\n{'='*60}")
        print("🖼️  EXTRACTING IMAGES FROM ALL JSON FILES")
        print(f"{'='*60}")
        self.run_extract_images_all(json_folder)
        
        # Step 3: Scrape CPM.js
        cpm_url = urljoin(base_url, "assets/js/CPM.js")
        self.scrape_and_save(
            cpm_url, 
            main_folder / "CPM.js", 
            "CPM.js file"
        )
        
        # Step 4: Scrape project.txt
        project_url = urljoin(base_url, "project.txt")
        self.scrape_and_save(
            project_url, 
            main_folder / "project.txt", 
            "project.txt file"
        )
        
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
    API_KEY = "fc-ba99fd9162ef43d38402cf2b903ca6cd"
    
    # Get URL from user input
    url = input("Enter the XML URL (ending with imsmanifest.xml): ").strip()
    
    if not url:
        print("Please provide a valid URL")
        return
    
    if not url.endswith('imsmanifest.xml'):
        print("Warning: URL doesn't end with 'imsmanifest.xml'")
    
    # Create scraper and process
    scraper = CourseContentScraper(API_KEY)
    scraper.process_course_url(url)


if __name__ == "__main__":
    main() 