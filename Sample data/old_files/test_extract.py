#!/usr/bin/env python3

import json
import base64
import os
import re
import sys

# Get the JSON file to process
json_file_path = 'JSON/dr_img1.json'

# Create output directory
os.makedirs('extracted_images', exist_ok=True)

with open(json_file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f'🎯 Image Extractor Test')
print(f'📁 Processing: {json_file_path}')
print(f'📄 File size: {len(content):,} bytes')

# Let's see what the content looks like
print(f'📄 First 500 characters of content:')
print(content[:500])
print('...')

# Extract the JSON object from cp.imagesJSONCache###={...}; (where ### can be any number)
pattern = r'cp\.imagesJSONCache\d+\s*=\s*(\{.*?\});'
match = re.search(pattern, content, re.DOTALL)

if match:
    json_str = match.group(1)
    print(f'✅ Found JSON pattern!')
    print(f'📄 JSON preview: {json_str[:200]}...')
    
    try:
        images_data = json.loads(json_str)
        
        print(f'🖼️  Found {len(images_data)} images')
        
        extracted_count = 0
        for filename, base64_data in images_data.items():
            try:
                # Clean filename (replace / with _)
                clean_filename = filename.replace('/', '_')
                if not clean_filename.endswith('.png'):
                    clean_filename += '.png'
                
                # Decode base64 data
                image_data = base64.b64decode(base64_data)
                
                # Save image
                output_path = os.path.join('extracted_images', clean_filename)
                with open(output_path, 'wb') as img_file:
                    img_file.write(image_data)
                
                print(f'✅ Extracted: {clean_filename} ({len(image_data):,} bytes)')
                extracted_count += 1
                
            except Exception as e:
                print(f'❌ Error extracting {filename}: {e}')
        
        print(f'🎉 Successfully extracted {extracted_count} images!')
        
    except json.JSONDecodeError as e:
        print(f'❌ JSON decode error: {e}')
        
else:
    print('❌ Could not find cp.imagesJSONCache pattern')
    print('Let me try other patterns...')
    
    # Try other potential patterns
    patterns_to_try = [
        r'imagesJSONCache.*?=\s*(\{.*?\});',
        r'images.*?=\s*(\{.*?\});',
        r'cache.*?=\s*(\{.*?\});',
        r'\{[^}]*"[^"]*\.(png|jpg|jpeg|gif)"[^}]*:[^}]*\}',
    ]
    
    for i, pattern in enumerate(patterns_to_try):
        print(f'Trying pattern {i+1}: {pattern}')
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f'✅ Found {len(matches)} matches with pattern {i+1}')
            for j, match in enumerate(matches[:3]):  # Show first 3 matches
                print(f'  Match {j+1}: {str(match)[:100]}...')
        else:
            print(f'❌ No matches for pattern {i+1}') 