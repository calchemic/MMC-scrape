#!/usr/bin/env python3

import csv
import time
from pathlib import Path

def load_bad_modules_list():
    """Load the list of lesson IDs from bad_modules.txt"""
    bad_modules_path = Path("scripts/bad_modules.txt")
    if not bad_modules_path.exists():
        print(f"❌ Error: {bad_modules_path} not found!")
        return set()
    
    bad_modules = set()
    with open(bad_modules_path, "r") as f:
        for line in f:
            lesson_id = line.strip()
            if lesson_id and not lesson_id.startswith('#'):  # Skip empty lines and comments
                bad_modules.add(lesson_id)
    
    print(f"📋 Loaded {len(bad_modules)} lesson IDs from bad_modules.txt")
    return bad_modules

def extract_bad_modules_csv():
    """Extract rows from main CSV that match bad_modules list"""
    
    print("="*80)
    print("🔧 BAD MODULES CSV EXTRACTOR")
    print("📋 CREATING FILTERED CSV WITH ONLY BAD MODULES")
    print("="*80)
    
    # Load the bad modules list
    bad_modules = load_bad_modules_list()
    if not bad_modules:
        print("❌ No bad modules found. Exiting.")
        return
    
    # Check if main CSV exists
    main_csv_path = "MMC Lessons All Simulation Lessons.csv"
    if not Path(main_csv_path).exists():
        print(f"❌ Error: {main_csv_path} not found!")
        return
    
    # Read main CSV and filter for bad modules
    print(f"📖 Reading main CSV: {main_csv_path}")
    
    matching_rows = []
    found_lesson_ids = set()
    total_rows = 0
    
    with open(main_csv_path, "r", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            total_rows += 1
            lesson_id = row.get("lessonID", "").strip()
            
            if lesson_id in bad_modules:
                matching_rows.append(row)
                found_lesson_ids.add(lesson_id)
                print(f"✅ Found: {lesson_id} - {row.get('lessonname', 'N/A')}")
    
    # Summary of what was found
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   • Total rows in main CSV: {total_rows}")
    print(f"   • Bad modules requested: {len(bad_modules)}")
    print(f"   • Matching rows found: {len(matching_rows)}")
    print(f"   • Success rate: {len(matching_rows)/len(bad_modules)*100:.1f}%")
    
    # Check for missing lesson IDs
    missing_lesson_ids = bad_modules - found_lesson_ids
    if missing_lesson_ids:
        print(f"\n⚠️  Missing lesson IDs (not found in main CSV): {len(missing_lesson_ids)}")
        print("First 10 missing IDs:")
        for i, missing_id in enumerate(sorted(missing_lesson_ids)):
            if i >= 10:
                print(f"   ... and {len(missing_lesson_ids) - 10} more")
                break
            print(f"   • {missing_id}")
    
    if not matching_rows:
        print("❌ No matching rows found. Check that lesson IDs in bad_modules.txt match those in the main CSV.")
        return
    
    # Create output CSV filename
    timestamp = int(time.time())
    output_filename = f"bad_modules_filtered_{len(matching_rows)}courses_{timestamp}.csv"
    
    # Write filtered CSV
    print(f"\n💾 Saving filtered CSV: {output_filename}")
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in matching_rows:
            writer.writerow(row)
    
    print(f"✅ Successfully created: {output_filename}")
    print(f"📋 Contains {len(matching_rows)} lesson records ready for processing")
    
    # Show a few sample rows
    if matching_rows:
        print(f"\n📋 Sample of extracted lessons:")
        for i, row in enumerate(matching_rows[:5]):
            lesson_id = row.get("lessonID", "N/A")
            lesson_name = row.get("lessonname", "N/A")
            url = row.get("link", "N/A")
            print(f"   {i+1}. {lesson_id} - {lesson_name}")
            print(f"      URL: {url}")
        
        if len(matching_rows) > 5:
            print(f"   ... and {len(matching_rows) - 5} more lessons")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   • Use {output_filename} for targeted scraping")
    print(f"   • This CSV contains only the {len(matching_rows)} lessons from your bad_modules.txt")
    print(f"   • You can now process this smaller CSV with any scraping tool")

if __name__ == "__main__":
    extract_bad_modules_csv() 