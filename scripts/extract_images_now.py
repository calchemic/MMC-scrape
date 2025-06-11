#!/usr/bin/env python3
"""
Extract images from the JSON file that contains the image data
"""

import json
import base64
import os
import re
import sys

def extract_images_from_json(json_file_path, output_dir):
    """Extract images from a JSON file containing image data"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f'❌ File not found: {json_file_path}')
        return 0
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f'🎯 Image Extractor')
    print(f'📁 Processing: {json_file_path}')
    print(f'📄 File size: {len(content):,} bytes')
    
    # Extract the JSON object from cp.imagesJSONCache###={...}; (where ### can be any number)
    pattern = r'cp\.imagesJSONCache\d+\s*=\s*(\{.*?\});'
    match = re.search(pattern, content, re.DOTALL)
    
    extracted_count = 0
    
    if match:
        json_str = match.group(1)
        try:
            images_data = json.loads(json_str)
            
            print(f'🖼️  Found {len(images_data)} images')
            
            for filename, base64_data in images_data.items():
                try:
                    # Skip empty filenames
                    if not filename.strip() or filename == '___':
                        continue
                        
                    # Clean filename (replace / with _)
                    clean_filename = filename.replace('/', '_')
                    if not clean_filename.endswith('.png'):
                        clean_filename += '.png'
                    
                    # Decode base64 data
                    if base64_data.strip():  # Only process non-empty base64 data
                        image_data = base64.b64decode(base64_data)
                        
                        # Only save if image data is not empty
                        if len(image_data) > 100:  # Skip very small files (likely corrupted)
                            # Save image
                            output_path = os.path.join(output_dir, clean_filename)
                            with open(output_path, 'wb') as img_file:
                                img_file.write(image_data)
                            
                            print(f'✅ Extracted: {clean_filename} ({len(image_data):,} bytes)')
                            extracted_count += 1
                        else:
                            print(f'⚠️  Skipped {filename} (too small: {len(image_data)} bytes)')
                    else:
                        print(f'⚠️  Skipped {filename} (empty base64 data)')
                        
                except Exception as e:
                    print(f'❌ Error extracting {filename}: {e}')
            
            print(f'🎉 Successfully extracted {extracted_count} images!')
            
        except json.JSONDecodeError as e:
            print(f'❌ JSON decode error: {e}')
            
    else:
        print('❌ Could not find cp.imagesJSONCache pattern')
    
    print(f'📁 Images saved to: {output_dir}/')
    return extracted_count

# Main execution
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 extract_images_now.py <json_file_path> <output_directory>")
        print("Example: python3 extract_images_now.py path/to/file.json extracted_images")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    extract_images_from_json(json_file_path, output_dir) 