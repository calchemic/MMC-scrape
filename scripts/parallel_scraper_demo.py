#!/usr/bin/env python3

import csv
import concurrent.futures
import time
from firecrawl_scraper import CourseContentScraper

def load_first_10_urls():
    """Load first 10 URLs from CSV"""
    urls = []
    with open("MMC Lessons All Simulation Lessons.csv", "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
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
    url_data, api_key, worker_id = args
    
    start_time = time.time()
    lesson_id = url_data["lesson_id"]
    
    try:
        print(f"🚀 Worker {worker_id}: Starting {lesson_id}")
        print(f"   API Key: {api_key[:20]}...")
        print(f"   URL: {url_data['url']}")
        
        # Create scraper with assigned API key
        scraper = CourseContentScraper(api_key)
        
        # Process the course URL
        result = scraper.process_course_url(url_data["url"])
        
        duration = time.time() - start_time
        print(f"✅ Worker {worker_id}: COMPLETED {lesson_id} in {duration:.1f}s")
        
        return {
            "worker_id": worker_id,
            "lesson_id": lesson_id,
            "status": "success",
            "duration": duration,
            "api_key": api_key[:20] + "..."
        }
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)[:100]  # Truncate long error messages
        print(f"❌ Worker {worker_id}: FAILED {lesson_id} in {duration:.1f}s")
        print(f"   Error: {error_msg}")
        
        return {
            "worker_id": worker_id,
            "lesson_id": lesson_id,
            "status": "failed",
            "duration": duration,
            "error": error_msg,
            "api_key": api_key[:20] + "..."
        }

def main():
    print("="*80)
    print("🚀 PARALLEL MMC COURSE SCRAPER - FIRST 10 URLS")
    print("="*80)
    
    # Load data
    urls = load_first_10_urls()
    api_keys = load_api_keys()
    
    print(f"📊 Configuration:")
    print(f"   • URLs to process: {len(urls)}")
    print(f"   • API keys available: {len(api_keys)}")
    print(f"   • Max parallel workers: {min(10, len(api_keys))}")
    print()
    
    # Show URL assignments
    print("📋 Course assignments:")
    for i, url_data in enumerate(urls):
        api_key = api_keys[i % len(api_keys)]
        print(f"   {i+1:2d}. {url_data['lesson_id']} → {api_key[:20]}...")
    print()
    
    # Create worker tasks (each gets a different API key)
    tasks = []
    for i, url_data in enumerate(urls):
        api_key = api_keys[i % len(api_keys)]  # Round-robin assignment
        worker_id = i + 1
        tasks.append((url_data, api_key, worker_id))
    
    # Start parallel processing
    print("🔧 Starting parallel processing...")
    start_time = time.time()
    
    max_workers = min(10, len(api_keys))  # Don't exceed available API keys
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(scrape_single_course, tasks))
    
    # Calculate results
    end_time = time.time()
    total_duration = end_time - start_time
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    # Print summary
    print("\n" + "="*80)
    print("📊 PARALLEL SCRAPING RESULTS")
    print("="*80)
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"⚡ Average time per URL: {total_duration/len(urls):.1f}s")
    
    if len(successful) > 0:
        avg_individual_time = sum(r["duration"] for r in successful) / len(successful)
        print(f"📈 Average individual processing time: {avg_individual_time:.1f}s")
        print(f"🚀 Speedup achieved: {avg_individual_time/total_duration*len(urls):.1f}x")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for result in sorted(results, key=lambda x: x["worker_id"]):
        status_emoji = "✅" if result["status"] == "success" else "❌"
        duration = result["duration"]
        lesson_id = result["lesson_id"]
        api_key = result["api_key"]
        
        print(f"   {status_emoji} Worker {result['worker_id']:2d}: {lesson_id:10s} ({duration:5.1f}s) - {api_key}")
        
        if "error" in result:
            print(f"      Error: {result['error']}")
    
    print(f"\n🎉 Parallel scraping completed in {total_duration:.1f}s!")
    print(f"💡 Sequential processing would have taken ~{sum(r['duration'] for r in results):.1f}s")

if __name__ == "__main__":
    main() 