#!/usr/bin/env python3
"""
Extract images from all dr_img*.json files in a folder using extract_images_now.py
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def extract_all_images(json_folder_path):
    """Extract images from all dr_img*.json files in the given folder"""
    
    # Convert to Path object for easier manipulation
    json_folder = Path(json_folder_path)
    
    if not json_folder.exists():
        print(f"❌ JSON folder not found: {json_folder_path}")
        return False
    
    # Get the parent folder (course folder) 
    course_folder = json_folder.parent
    extracted_images_folder = course_folder / "extracted_images"
    
    print(f"🎯 Batch Image Extractor")
    print(f"📁 JSON folder: {json_folder}")
    print(f"📁 Course folder: {course_folder}")
    print(f"📁 Output folder: {extracted_images_folder}")
    
    # Find all dr_img*.json files
    pattern = str(json_folder / "dr_img*.json")
    json_files = glob.glob(pattern)
    json_files.sort()  # Sort to process in order
    
    if not json_files:
        print(f"❌ No dr_img*.json files found in {json_folder}")
        return False
    
    print(f"🔍 Found {len(json_files)} dr_img*.json files:")
    for json_file in json_files:
        print(f"   - {Path(json_file).name}")
    
    # Create output directory
    extracted_images_folder.mkdir(exist_ok=True)
    
    # Get the directory where this script is located to find extract_images_now.py
    script_dir = Path(__file__).parent
    extract_script = script_dir / "extract_images_now.py"
    
    if not extract_script.exists():
        print(f"❌ extract_images_now.py not found at: {extract_script}")
        return False
    
    # Process each JSON file
    total_extracted = 0
    successful_files = 0
    
    for json_file in json_files:
        json_path = Path(json_file)
        print(f"\n{'='*60}")
        print(f"🎯 Processing: {json_path.name}")
        
        try:
            # Run extract_images_now.py on this file
            result = subprocess.run([
                'python3', str(extract_script),
                str(json_path),
                str(extracted_images_folder)
            ], capture_output=True, text=True, cwd=script_dir)
            
            if result.returncode == 0:
                # Count how many images were extracted from the output
                if "Successfully extracted" in result.stdout:
                    # Extract the number from the output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Successfully extracted" in line and "images!" in line:
                            try:
                                # Extract number from line like "🎉 Successfully extracted 25 images!"
                                import re
                                match = re.search(r'Successfully extracted (\d+) images', line)
                                if match:
                                    count = int(match.group(1))
                                    total_extracted += count
                                    print(f"✅ Extracted {count} images from {json_path.name}")
                                    break
                            except:
                                pass
                
                successful_files += 1
                print(result.stdout)
            else:
                print(f"❌ Error processing {json_path.name}:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Exception processing {json_path.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"🎉 EXTRACTION COMPLETE!")
    print(f"📊 Successfully processed: {successful_files}/{len(json_files)} files")
    print(f"🖼️  Total images extracted: {total_extracted}")
    print(f"📁 Images saved to: {extracted_images_folder}")
    
    return successful_files > 0

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 extract_images_all.py <json_folder_path>")
        print("Example: python3 extract_images_all.py /path/to/course/JSON")
        sys.exit(1)
    
    json_folder_path = sys.argv[1]
    success = extract_all_images(json_folder_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 