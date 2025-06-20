#!/usr/bin/env python3

import csv
import concurrent.futures
import time
import argparse
from fixed_scraper import CourseContentScraper

def load_all_urls(limit=None):
    """Load URLs from CSV with optional limit"""
    urls = []
    with open("bad_modules_filtered_962courses_1750444941.csv", "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Apply limit if specified
            if limit and i >= limit:
                break
            urls.append({
                "url": row["link"],
                "lesson_id": row["lessonID"],
                "lesson_name": row["lessonname"]
            })
    return urls

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
            "api_key": api_key[:20] + "..."
        }
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)[:200]  # Increased error message length for better debugging
        print(f"❌ Batch {batch_num} | Worker {worker_id}: FAILED {lesson_id} in {duration:.1f}s")
        print(f"   Error: {error_msg}")
        
        return {
            "batch_num": batch_num,
            "worker_id": worker_id,
            "lesson_id": lesson_id,
            "status": "failed",
            "duration": duration,
            "error": error_msg,
            "api_key": api_key[:20] + "..."
        }

def process_batch(batch_urls, api_keys, batch_num, total_batches):
    """Process a single batch of courses"""
    print(f"\n{'='*80}")
    print(f"🔥 PROCESSING BATCH {batch_num}/{total_batches}")
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
    
    # Wait a bit between batches to respect rate limits
    if batch_num < total_batches:
        wait_time = 30  # 30 seconds between batches
        print(f"\n⏸️  Waiting {wait_time}s before next batch to respect rate limits...")
        time.sleep(wait_time)
    
    return batch_results

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MMC Course Scraper with Batch Processing')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Limit the number of courses to process (useful for testing)')
    args = parser.parse_args()
    
    # Determine run type
    run_type = "TESTING" if args.limit else "FULL PRODUCTION"
    course_count_text = f"FIRST {args.limit} COURSES" if args.limit else "ALL 1,536 COURSES"
    
    print("="*80)
    print(f"🚀 PARALLEL MMC COURSE SCRAPER - {run_type}")
    print(f"📋 PROCESSING: {course_count_text}")
    print("="*80)
    
    # Load data
    urls = load_all_urls(limit=args.limit)
    api_keys = load_api_keys()
    
    print(f"📊 Configuration:")
    print(f"   • Total URLs to process: {len(urls)}")
    if args.limit:
        print(f"   • 🧪 TESTING MODE: Limited to first {args.limit} courses")
    else:
        print(f"   • 🏭 PRODUCTION MODE: Processing all courses")
    print(f"   • API keys available: {len(api_keys)}")
    
    # Calculate batches
    batch_size = len(api_keys)  # One batch = one course per API key
    total_batches = (len(urls) + batch_size - 1) // batch_size  # Ceiling division
    
    print(f"   • Batch size: {batch_size} courses per batch")
    print(f"   • Total batches: {total_batches}")
    print(f"   • Processing strategy: Complete each batch fully before next")
    
    if args.limit and args.limit <= 68:
        print(f"   • 💡 Note: With {args.limit} courses, all will fit in 1 batch!")
    
    print()
    
    # Show first few courses that will be processed
    print("📋 Courses to be processed:")
    display_count = min(10, len(urls))
    for i in range(display_count):
        print(f"   {i+1:2d}. {urls[i]['lesson_id']} - {urls[i]['lesson_name']}")
    if len(urls) > display_count:
        print(f"   ... and {len(urls) - display_count} more courses")
    print()
    
    # Confirmation for testing mode
    if args.limit:
        print(f"🧪 TESTING MODE ACTIVE - Processing only {args.limit} courses")
        print("   This is perfect for testing the batch processing system!")
        print()
    
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
        print(f"\n🎯 OVERALL PROGRESS: {courses_completed}/{len(urls)} courses ({progress_pct:.1f}%)")
    
    # Final results
    total_duration = time.time() - total_start_time
    successful = [r for r in all_results if r["status"] == "success"]
    failed = [r for r in all_results if r["status"] == "failed"]
    
    print("\n" + "="*80)
    if args.limit:
        print(f"🧪 TESTING RESULTS ({args.limit} COURSES)")
    else:
        print("🎉 FINAL BATCH PROCESSING RESULTS")
    print("="*80)
    
    print(f"✅ Total Successful: {len(successful)}/{len(urls)}")
    print(f"❌ Total Failed: {len(failed)}/{len(urls)}")
    print(f"📈 Success Rate: {(len(successful)/len(urls)*100):.1f}%")
    print(f"⏱️  Total processing time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"⚡ Average time per course: {total_duration/len(urls):.1f}s")
    
    if len(successful) > 0:
        avg_individual_time = sum(r["duration"] for r in successful) / len(successful)
        print(f"📊 Average individual processing time: {avg_individual_time:.1f}s")
        theoretical_sequential = avg_individual_time * len(urls)
        actual_speedup = theoretical_sequential / total_duration
        print(f"🚀 Speedup achieved: {actual_speedup:.1f}x vs sequential processing")
    
    # Batch performance summary
    print(f"\n📋 Batch Performance Summary:")
    batch_stats = {}
    for result in all_results:
        batch_num = result["batch_num"]
        if batch_num not in batch_stats:
            batch_stats[batch_num] = {"success": 0, "failed": 0}
        batch_stats[batch_num][result["status"]] += 1
    
    for batch_num in sorted(batch_stats.keys()):
        stats = batch_stats[batch_num]
        total_in_batch = stats["success"] + stats["failed"]
        success_rate = (stats["success"] / total_in_batch * 100) if total_in_batch > 0 else 0
        print(f"   Batch {batch_num:2d}: {stats['success']:3d} ✅ | {stats['failed']:3d} ❌ | {success_rate:5.1f}% success")
    
    # Save results to CSV
    print("\n💾 Saving results to CSV...")
    if args.limit:
        csv_filename = f"scraping_results_test_{args.limit}courses_{int(time.time())}.csv"
    else:
        csv_filename = f"scraping_results_batch_{int(time.time())}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['batch_num', 'worker_id', 'lesson_id', 'status', 'duration', 'api_key', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in sorted(all_results, key=lambda x: (x["batch_num"], x["worker_id"])):
            writer.writerow({
                'batch_num': result['batch_num'],
                'worker_id': result['worker_id'],
                'lesson_id': result['lesson_id'],
                'status': result['status'],
                'duration': result['duration'],
                'api_key': result['api_key'],
                'error': result.get('error', '')
            })
    
    print(f"✅ Results saved to: {csv_filename}")
    
    if args.limit:
        print(f"\n🧪 Testing completed in {total_duration:.1f}s!")
        print(f"💡 To run full production: python scripts/parallel_scraper_full.py")
        print(f"🔧 To test with different limit: python scripts/parallel_scraper_full.py --limit 25")
    else:
        print(f"\n🎉 Batch processing completed in {total_duration:.1f}s!")
    
    if failed:
        print(f"\n⚠️  {len(failed)} courses failed - check CSV for details")
        print("💡 Failed courses can be reprocessed individually if needed")

if __name__ == "__main__":
    main() 