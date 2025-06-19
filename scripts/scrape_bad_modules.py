#!/usr/bin/env python3

import csv
import concurrent.futures
import time
import argparse
from pathlib import Path
from fixed_scraper import CourseContentScraper

def load_bad_modules_list():
    """Load the list of lesson IDs that need to be scraped from bad_modules.txt"""
    bad_modules_path = Path("scripts/bad_modules.txt")
    if not bad_modules_path.exists():
        print(f"❌ Error: {bad_modules_path} not found!")
        return []
    
    bad_modules = []
    with open(bad_modules_path, "r") as f:
        for line in f:
            lesson_id = line.strip()
            if lesson_id and not lesson_id.startswith('#'):  # Skip empty lines and comments
                bad_modules.append(lesson_id)
    
    print(f"📋 Loaded {len(bad_modules)} lesson IDs from bad_modules.txt")
    return bad_modules

def load_matching_urls_from_csv(bad_modules_list, limit=None):
    """Load URLs from main CSV that match the lesson IDs in bad_modules.txt"""
    csv_path = "MMC Lessons All Simulation Lessons.csv"
    if not Path(csv_path).exists():
        print(f"❌ Error: {csv_path} not found!")
        return []
    
    bad_modules_set = set(bad_modules_list)
    matching_urls = []
    not_found = set(bad_modules_list)  # Track which modules we couldn't find
    
    print(f"🔍 Searching main CSV for {len(bad_modules_set)} lesson IDs...")
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lesson_id = row["lessonID"]
            if lesson_id in bad_modules_set:
                # Apply limit if specified
                if limit and len(matching_urls) >= limit:
                    break
                    
                matching_urls.append({
                    "url": row["link"],
                    "lesson_id": lesson_id,
                    "lesson_name": row["lessonname"],
                    "course_id": row["courseid"],
                    "course_name": row["coursename"]
                })
                not_found.discard(lesson_id)  # Remove from not_found set
    
    print(f"✅ Found {len(matching_urls)} matching URLs in main CSV")
    
    if not_found:
        print(f"⚠️  Warning: {len(not_found)} lesson IDs from bad_modules.txt were not found in the main CSV:")
        for lesson_id in sorted(list(not_found))[:10]:  # Show first 10
            print(f"   • {lesson_id}")
        if len(not_found) > 10:
            print(f"   ... and {len(not_found) - 10} more")
    
    return matching_urls

def load_api_keys():
    """Load API keys from file"""
    with open("API keys.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def scrape_single_course(args):
    """Scrape a single course with assigned API key"""
    url_data, api_key, worker_id, batch_num = args
    
    start_time = time.time()
    lesson_id = url_data["lesson_id"]
    
    try:
        print(f"🚀 Batch {batch_num} | Worker {worker_id}: Starting {lesson_id}")
        print(f"   API Key: {api_key[:20]}...")
        print(f"   URL: {url_data['url']}")
        
        # Create scraper with assigned API key
        scraper = CourseContentScraper(api_key)
        
        # Process the course URL
        result = scraper.process_course_url(url_data["url"])
        
        duration = time.time() - start_time
        print(f"✅ Batch {batch_num} | Worker {worker_id}: COMPLETED {lesson_id} in {duration:.1f}s")
        
        return {
            "batch_num": batch_num,
            "worker_id": worker_id,
            "lesson_id": lesson_id,
            "status": "success",
            "duration": duration,
            "api_key": api_key[:20] + "...",
            "course_id": url_data.get("course_id", ""),
            "course_name": url_data.get("course_name", "")
        }
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)[:200]
        print(f"❌ Batch {batch_num} | Worker {worker_id}: FAILED {lesson_id} in {duration:.1f}s")
        print(f"   Error: {error_msg}")
        
        return {
            "batch_num": batch_num,
            "worker_id": worker_id,
            "lesson_id": lesson_id,
            "status": "failed",
            "duration": duration,
            "error": error_msg,
            "api_key": api_key[:20] + "...",
            "course_id": url_data.get("course_id", ""),
            "course_name": url_data.get("course_name", "")
        }

def process_batch(batch_urls, api_keys, batch_num, total_batches):
    """Process a single batch of courses"""
    print(f"\n{'='*80}")
    print(f"🔥 PROCESSING BATCH {batch_num}/{total_batches} - BAD MODULES SCRAPING")
    print(f"{'='*80}")
    print(f"📊 Batch info:")
    print(f"   • Courses in this batch: {len(batch_urls)}")
    print(f"   • API keys to use: {min(len(batch_urls), len(api_keys))}")
    print()
    
    # Show batch course assignments
    print("📋 Batch course assignments:")
    for i, url_data in enumerate(batch_urls):
        api_key = api_keys[i % len(api_keys)]
        print(f"   {i+1:2d}. {url_data['lesson_id']} → {api_key[:20]}...")
    print()
    
    # Create tasks for this batch
    tasks = []
    for i, url_data in enumerate(batch_urls):
        api_key = api_keys[i % len(api_keys)]
        worker_id = i + 1
        tasks.append((url_data, api_key, worker_id, batch_num))
    
    # Process this batch
    batch_start_time = time.time()
    max_workers = min(len(batch_urls), len(api_keys))
    
    print(f"🔧 Starting batch {batch_num} with {max_workers} parallel workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        batch_results = list(executor.map(scrape_single_course, tasks))
    
    batch_duration = time.time() - batch_start_time
    
    # Batch summary
    successful = [r for r in batch_results if r["status"] == "success"]
    failed = [r for r in batch_results if r["status"] == "failed"]
    
    print(f"\n📊 BATCH {batch_num} SUMMARY:")
    print(f"✅ Successful: {len(successful)}/{len(batch_urls)}")
    print(f"❌ Failed: {len(failed)}/{len(batch_urls)}")
    print(f"⏱️  Batch time: {batch_duration:.1f}s")
    print(f"⚡ Average time per course: {batch_duration/len(batch_urls):.1f}s")
    
    if failed:
        print("\n❌ Failed courses in this batch:")
        for result in failed:
            print(f"   • {result['lesson_id']}: {result['error'][:100]}...")
    
    # Wait between batches to respect rate limits
    if batch_num < total_batches:
        wait_time = 30  # 30 seconds between batches
        print(f"\n⏸️  Waiting {wait_time}s before next batch to respect rate limits...")
        time.sleep(wait_time)
    
    return batch_results

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape the 964 bad modules from bad_modules.txt')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Limit the number of bad modules to process (useful for testing)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Just show what would be processed without actually scraping')
    args = parser.parse_args()
    
    print("="*80)
    print("🔧 BAD MODULES SCRAPER - TARGETED PROCESSING")
    print(f"📋 PROCESSING FAILED/MISSING MODULES FROM bad_modules.txt")
    print("="*80)
    
    # Load bad modules list
    bad_modules_list = load_bad_modules_list()
    if not bad_modules_list:
        print("❌ No modules to process. Exiting.")
        return
    
    # Load matching URLs from CSV
    urls = load_matching_urls_from_csv(bad_modules_list, limit=args.limit)
    if not urls:
        print("❌ No matching URLs found. Exiting.")
        return
    
    # Load API keys
    api_keys = load_api_keys()
    
    print(f"📊 Configuration:")
    print(f"   • Bad modules in file: {len(bad_modules_list)}")
    print(f"   • URLs found in CSV: {len(urls)}")
    if args.limit:
        print(f"   • 🧪 TESTING MODE: Limited to first {args.limit} modules")
    else:
        print(f"   • 🏭 PRODUCTION MODE: Processing all {len(urls)} found modules")
    print(f"   • API keys available: {len(api_keys)}")
    
    # Calculate batches
    batch_size = len(api_keys)
    total_batches = (len(urls) + batch_size - 1) // batch_size
    
    print(f"   • Batch size: {batch_size} courses per batch")
    print(f"   • Total batches: {total_batches}")
    print()
    
    # Show sample of courses to be processed
    print("📋 Sample of courses to be processed:")
    display_count = min(10, len(urls))
    for i in range(display_count):
        print(f"   {i+1:2d}. {urls[i]['lesson_id']} - {urls[i]['lesson_name']}")
    if len(urls) > display_count:
        print(f"   ... and {len(urls) - display_count} more courses")
    print()
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - Would process these courses but not actually scraping")
        print("✅ Dry run complete. Remove --dry-run to start actual scraping.")
        return
    
    if args.limit:
        print(f"🧪 TESTING MODE ACTIVE - Processing only {args.limit} bad modules")
        print("   This is perfect for testing the bad modules processing!")
    
    # Process all batches
    all_results = []
    total_start_time = time.time()
    
    for batch_num in range(1, total_batches + 1):
        # Get courses for this batch
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(urls))
        batch_urls = urls[start_idx:end_idx]
        
        # Process this batch
        batch_results = process_batch(batch_urls, api_keys, batch_num, total_batches)
        all_results.extend(batch_results)
        
        # Progress update
        courses_completed = len(all_results)
        progress_pct = (courses_completed / len(urls)) * 100
        print(f"\n🎯 OVERALL PROGRESS: {courses_completed}/{len(urls)} bad modules ({progress_pct:.1f}%)")
    
    # Final results
    total_duration = time.time() - total_start_time
    successful = [r for r in all_results if r["status"] == "success"]
    failed = [r for r in all_results if r["status"] == "failed"]
    
    print("\n" + "="*80)
    print("🎉 BAD MODULES SCRAPING RESULTS")
    print("="*80)
    
    print(f"✅ Total Successful: {len(successful)}/{len(urls)}")
    print(f"❌ Total Failed: {len(failed)}/{len(urls)}")
    print(f"📈 Success Rate: {(len(successful)/len(urls)*100):.1f}%")
    print(f"⏱️  Total processing time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"⚡ Average time per module: {total_duration/len(urls):.1f}s")
    
    if len(successful) > 0:
        avg_individual_time = sum(r["duration"] for r in successful) / len(successful)
        print(f"📊 Average individual processing time: {avg_individual_time:.1f}s")
        theoretical_sequential = avg_individual_time * len(urls)
        actual_speedup = theoretical_sequential / total_duration
        print(f"🚀 Speedup achieved: {actual_speedup:.1f}x vs sequential processing")
    
    # Save results to CSV
    print("\n💾 Saving results to CSV...")
    if args.limit:
        csv_filename = f"bad_modules_results_test_{args.limit}modules_{int(time.time())}.csv"
    else:
        csv_filename = f"bad_modules_results_all_{int(time.time())}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['batch_num', 'worker_id', 'lesson_id', 'course_id', 'course_name', 'status', 'duration', 'api_key', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in sorted(all_results, key=lambda x: (x["batch_num"], x["worker_id"])):
            writer.writerow({
                'batch_num': result['batch_num'],
                'worker_id': result['worker_id'],
                'lesson_id': result['lesson_id'],
                'course_id': result.get('course_id', ''),
                'course_name': result.get('course_name', ''),
                'status': result['status'],
                'duration': result['duration'],
                'api_key': result['api_key'],
                'error': result.get('error', '')
            })
    
    print(f"✅ Results saved to: {csv_filename}")
    
    # Save failed modules to text file for easy retry
    if failed:
        print("\n📝 Saving failed modules to text file...")
        if args.limit:
            failed_filename = f"failed_modules_test_{args.limit}modules_{int(time.time())}.txt"
            failed_details_filename = f"failed_modules_details_test_{args.limit}modules_{int(time.time())}.txt"
        else:
            failed_filename = f"failed_modules_{int(time.time())}.txt"
            failed_details_filename = f"failed_modules_details_{int(time.time())}.txt"
        
        # Save just the lesson IDs for easy retry
        with open(failed_filename, 'w', encoding='utf-8') as f:
            f.write("# Failed modules from bad_modules scraping\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total failed: {len(failed)}\n")
            f.write("# You can copy these lesson IDs back to bad_modules.txt to retry\n\n")
            for result in sorted(failed, key=lambda x: x["lesson_id"]):
                f.write(f"{result['lesson_id']}\n")
        
        # Save detailed error information
        with open(failed_details_filename, 'w', encoding='utf-8') as f:
            f.write("# Detailed failure information for bad_modules scraping\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total failed: {len(failed)}\n\n")
            for result in sorted(failed, key=lambda x: x["lesson_id"]):
                f.write(f"Lesson ID: {result['lesson_id']}\n")
                f.write(f"Course ID: {result.get('course_id', 'N/A')}\n")
                f.write(f"Course Name: {result.get('course_name', 'N/A')}\n")
                f.write(f"Batch: {result['batch_num']}, Worker: {result['worker_id']}\n")
                f.write(f"Duration: {result['duration']:.1f}s\n")
                f.write(f"Error: {result.get('error', 'No error details')}\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"✅ Failed modules list saved to: {failed_filename}")
        print(f"✅ Failed modules details saved to: {failed_details_filename}")
        print(f"💡 To retry only failed modules, copy content from {failed_filename} to bad_modules.txt")
    
    if args.limit:
        print(f"\n🧪 Testing completed in {total_duration:.1f}s!")
        print(f"💡 To run full bad modules processing: python scripts/scrape_bad_modules.py")
        print(f"🔧 To test with different limit: python scripts/scrape_bad_modules.py --limit 25")
    else:
        print(f"\n🎉 Bad modules scraping completed in {total_duration:.1f}s!")
    
    if failed:
        print(f"\n⚠️  {len(failed)} modules failed - check CSV and failed_modules_*.txt files for details")
        print("💡 Failed modules can be reprocessed by updating bad_modules.txt and running again")
    
    # Summary of what was accomplished
    print(f"\n📋 SUMMARY:")
    print(f"   • Started with {len(bad_modules_list)} lesson IDs in bad_modules.txt")
    print(f"   • Found {len(urls)} matching URLs in main CSV")
    print(f"   • Successfully scraped {len(successful)} modules")
    print(f"   • {len(failed)} modules still need attention")
    
    if failed:
        print(f"\n💡 TIP: Failed lesson IDs have been saved to failed_modules_*.txt files.")
        print(f"   You can copy the content from failed_modules_*.txt to bad_modules.txt to retry only failed modules.")

if __name__ == "__main__":
    main() 